"""Build a reproducible county behavioral-health prioritization analysis.

Data sources
------------
CDC PLACES County Data (GIS-friendly), 2025 release: i46a-9kgh
U.S. Census Bureau 2025 county cartographic boundary file (1:500,000)

This workflow uses rank-based descriptive screening. It does not estimate causal
effects, diagnose individuals, or evaluate local programs.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import duckdb
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
QA = ROOT / "outputs" / "qa_report.json"

PLACES_API = "https://data.cdc.gov/resource/i46a-9kgh.csv"
PLACES_PAGE = (
    "https://data.cdc.gov/500-Cities-Places/"
    "PLACES-County-Data-GIS-Friendly-Format-2025-release/i46a-9kgh"
)
CENSUS_ZIP = (
    "https://www2.census.gov/geo/tiger/GENZ2025/shp/"
    "cb_2025_us_county_500k.zip"
)

KEEP = [
    "stateabbr",
    "statedesc",
    "countyname",
    "countyfips",
    "totalpopulation",
    "totalpop18plus",
    "depression_adjprev",
    "depression_adj95ci",
    "mhlth_adjprev",
    "mhlth_adj95ci",
    "access2_adjprev",
    "access2_adj95ci",
]

NAVY = "#15324a"
TEAL = "#1f8a89"
GOLD = "#f2b134"
RED = "#c44e52"
PALE = "#eef3f6"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, path: Path, *, params: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    path.write_bytes(response.content)


def acquire() -> tuple[Path, Path]:
    places = RAW / "cdc_places_county_2025_selected.csv"
    census = RAW / "cb_2025_us_county_500k.zip"
    download(
        PLACES_API,
        places,
        params={"$select": ",".join(KEEP), "$limit": 5000, "$order": "countyfips"},
    )
    download(CENSUS_ZIP, census)
    return places, census


def clean_and_rank(places_path: Path) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    raw = pd.read_csv(places_path, dtype={"countyfips": "string"})
    raw["countyfips"] = raw["countyfips"].str.zfill(5)
    numeric = [
        "totalpopulation",
        "totalpop18plus",
        "depression_adjprev",
        "mhlth_adjprev",
        "access2_adjprev",
    ]
    for col in numeric:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")

    con = duckdb.connect()
    con.register("raw_places", raw)
    validation = con.execute(
        """
        SELECT
          COUNT(*) AS rows,
          COUNT(DISTINCT countyfips) AS unique_counties,
          SUM(CASE WHEN countyfips IS NULL OR length(countyfips) <> 5 THEN 1 ELSE 0 END) AS bad_fips,
          SUM(CASE WHEN depression_adjprev IS NULL THEN 1 ELSE 0 END) AS missing_depression,
          SUM(CASE WHEN mhlth_adjprev IS NULL THEN 1 ELSE 0 END) AS missing_mhlth,
          SUM(CASE WHEN access2_adjprev IS NULL THEN 1 ELSE 0 END) AS missing_access,
          SUM(CASE WHEN depression_adjprev IS NOT NULL AND mhlth_adjprev IS NOT NULL
                    AND access2_adjprev IS NOT NULL THEN 1 ELSE 0 END) AS complete_components,
          SUM(CASE WHEN depression_adjprev NOT BETWEEN 0 AND 100 THEN 1 ELSE 0 END) AS bad_depression,
          SUM(CASE WHEN mhlth_adjprev NOT BETWEEN 0 AND 100 THEN 1 ELSE 0 END) AS bad_mhlth,
          SUM(CASE WHEN access2_adjprev NOT BETWEEN 0 AND 100 THEN 1 ELSE 0 END) AS bad_access
        FROM raw_places
        """
    ).df().iloc[0].to_dict()

    ranked = con.execute((SQL / "priority_scoring.sql").read_text(encoding="utf-8")).df()
    con.close()

    ranked["priority_decile"] = pd.qcut(
        ranked["priority_score"], 10, labels=False, duplicates="drop"
    ) + 1
    ranked["priority_tier"] = np.select(
        [ranked["priority_decile"] == 10, ranked["priority_decile"] >= 8],
        ["Highest priority signal", "Elevated priority signal"],
        default="Comparison",
    )
    ranked["county_label"] = ranked["countyname"] + ", " + ranked["stateabbr"]
    assert len(raw) == raw["countyfips"].nunique(), "County FIPS must be unique"
    assert all(float(validation[k]) == 0 for k in ["bad_fips", "bad_depression", "bad_mhlth", "bad_access"])
    assert ranked["priority_score"].between(0, 100).all()
    missing = raw[
        raw[["depression_adjprev", "mhlth_adjprev", "access2_adjprev"]].isna().any(axis=1)
    ]
    missing_by_state = (
        missing.groupby(["stateabbr", "statedesc"], as_index=False)
        .agg(counties_missing_any_component=("countyfips", "size"))
        .sort_values("counties_missing_any_component", ascending=False)
    )
    return ranked, validation, missing_by_state


def build_geodata(ranked: pd.DataFrame, census_zip: Path) -> gpd.GeoDataFrame:
    extract_dir = RAW / "census_counties_2025"
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(census_zip) as zf:
        zf.extractall(extract_dir)
    shp = next(extract_dir.glob("*.shp"))
    counties = gpd.read_file(shp)[["GEOID", "NAME", "STUSPS", "geometry"]]
    gdf = counties.merge(
        ranked,
        left_on="GEOID",
        right_on="countyfips",
        how="inner",
        validate="one_to_one",
    )
    return gdf


def weighted_mean(frame: pd.DataFrame, value: str, weight: str) -> float:
    ok = frame[value].notna() & frame[weight].notna() & (frame[weight] > 0)
    return float(np.average(frame.loc[ok, value], weights=frame.loc[ok, weight]))


def summarize(ranked: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    high = ranked[ranked["priority_decile"] == 10].copy()
    rest = ranked[ranked["priority_decile"] < 10].copy()
    top_counties = high.sort_values(["priority_score", "countyfips"], ascending=[False, True])
    state_summary = (
        high.groupby(["stateabbr", "statedesc"], as_index=False)
        .agg(
            highest_priority_counties=("countyfips", "size"),
            population_represented=("totalpopulation", "sum"),
            median_priority_score=("priority_score", "median"),
        )
        .sort_values(["highest_priority_counties", "median_priority_score"], ascending=False)
    )
    metrics = {
        "eligible_counties": int(len(ranked)),
        "highest_priority_counties": int(len(high)),
        "population_in_highest_priority_counties": int(high["totalpopulation"].sum()),
        "weighted_depression_highest_decile": weighted_mean(high, "depression_adjprev", "totalpop18plus"),
        "weighted_depression_other_counties": weighted_mean(rest, "depression_adjprev", "totalpop18plus"),
        "weighted_distress_highest_decile": weighted_mean(high, "mhlth_adjprev", "totalpop18plus"),
        "weighted_distress_other_counties": weighted_mean(rest, "mhlth_adjprev", "totalpop18plus"),
        "weighted_uninsured_highest_decile": weighted_mean(high, "access2_adjprev", "totalpopulation"),
        "weighted_uninsured_other_counties": weighted_mean(rest, "access2_adjprev", "totalpopulation"),
        "depression_distress_pearson_r": float(ranked[["depression_adjprev", "mhlth_adjprev"]].corr().iloc[0, 1]),
        "priority_score_cutpoint_top_decile": float(high["priority_score"].min()),
    }
    return top_counties, state_summary, metrics


def plot_map(gdf: gpd.GeoDataFrame, path: Path) -> None:
    conus = gdf[~gdf["STUSPS"].isin(["AK", "HI", "PR", "VI", "GU", "MP", "AS"])].copy()
    cmap = LinearSegmentedColormap.from_list("priority", [PALE, TEAL, GOLD, RED])
    fig, ax = plt.subplots(figsize=(13, 8), facecolor="white")
    conus.plot(
        column="priority_score",
        cmap=cmap,
        linewidth=0.08,
        edgecolor="white",
        vmin=0,
        vmax=100,
        legend=True,
        legend_kwds={"label": "Behavioral-health priority score (percentile average)", "shrink": 0.62},
        ax=ax,
    )
    fig.suptitle(
        "County behavioral-health priority signals",
        x=0.01,
        y=0.98,
        ha="left",
        fontsize=20,
        fontweight="bold",
        color=NAVY,
    )
    fig.text(
        0.01,
        0.935,
        "Higher values combine depression, frequent mental distress and lack of insurance estimates",
        fontsize=10.5,
        color="#4d6573",
    )
    ax.axis("off")
    fig.text(
        0.01,
        0.02,
        "CDC PLACES 2025 release; Census 2025 boundaries. Screening signal only. Kentucky and Pennsylvania lack complete inputs and appear white.",
        fontsize=8.5,
        color="#5d6b73",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.91])
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_top(top: pd.DataFrame, path: Path) -> None:
    show = top.head(15).sort_values("priority_score")
    fig, ax = plt.subplots(figsize=(10, 7), facecolor="white")
    colors = plt.cm.YlOrRd((show["priority_score"] - 70) / 30)
    ax.barh(show["county_label"], show["priority_score"], color=colors)
    ax.set_xlim(70, 100)
    ax.set_xlabel("Composite percentile score")
    ax.set_title("Highest composite signals among eligible counties", loc="left", fontsize=17, fontweight="bold", color=NAVY)
    ax.grid(axis="x", color="#dce5e9", linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_scatter(ranked: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 7), facecolor="white")
    sc = ax.scatter(
        ranked["depression_adjprev"],
        ranked["mhlth_adjprev"],
        c=ranked["access2_adjprev"],
        s=np.clip(np.sqrt(ranked["totalpopulation"]) / 3, 8, 80),
        cmap="viridis",
        alpha=0.68,
        linewidth=0,
    )
    ax.set_xlabel("Depression, age-adjusted prevalence (%)")
    ax.set_ylabel("Frequent mental distress, age-adjusted prevalence (%)")
    ax.set_title("Behavioral-health indicators move together, but access risk varies", loc="left", fontsize=16, fontweight="bold", color=NAVY)
    cb = fig.colorbar(sc, ax=ax, shrink=0.82)
    cb.set_label("Lack of insurance, age-adjusted prevalence (%)")
    ax.grid(color="#e2e9ec", linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_preview(metrics: dict, top: pd.DataFrame, path: Path) -> None:
    fig = plt.figure(figsize=(14, 8), facecolor="#f7fafb")
    gs = fig.add_gridspec(2, 3, height_ratios=[0.42, 1], wspace=0.28, hspace=0.25)
    cards = [
        (f"{metrics['eligible_counties']:,}", "counties with complete inputs"),
        (f"{metrics['highest_priority_counties']:,}", "counties in highest signal decile"),
        (f"{metrics['depression_distress_pearson_r']:.2f}", "depression-distress correlation"),
    ]
    for i, (number, label) in enumerate(cards):
        ax = fig.add_subplot(gs[0, i])
        ax.set_facecolor("white")
        ax.text(0.05, 0.62, number, fontsize=29, fontweight="bold", color=TEAL, transform=ax.transAxes)
        ax.text(0.05, 0.25, label, fontsize=10.5, color="#4d6573", transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#dce5e9")

    ax = fig.add_subplot(gs[1, :])
    show = top.head(12).sort_values("priority_score")
    ax.barh(show["county_label"], show["priority_score"], color=GOLD)
    ax.set_xlim(70, 100)
    ax.set_xlabel("Composite percentile score")
    ax.grid(axis="x", color="#dce5e9", linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    fig.suptitle("Where behavioral-health need and coverage gaps overlap", x=0.055, y=0.99, ha="left", fontsize=22, fontweight="bold", color=NAVY)
    fig.text(0.055, 0.945, "A transparent county screening workflow using CDC PLACES, DuckDB SQL, Python and GIS", fontsize=11.5, color="#4d6573")
    fig.text(0.055, 0.015, "Descriptive priority signal only. PLACES estimates are model-based and should not be used to evaluate local programs.", fontsize=8.5, color="#5d6b73")
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_outputs(
    ranked: pd.DataFrame,
    gdf: gpd.GeoDataFrame,
    validation: dict,
    missing_by_state: pd.DataFrame,
    raw_paths: tuple[Path, Path],
) -> dict:
    for folder in [PROCESSED, TABLES, FIGURES]:
        folder.mkdir(parents=True, exist_ok=True)
    top, states, metrics = summarize(ranked)
    ranked.to_csv(PROCESSED / "county_priority_scores.csv", index=False)
    top.to_csv(TABLES / "highest_priority_counties.csv", index=False)
    states.to_csv(TABLES / "highest_priority_counties_by_state.csv", index=False)
    missing_by_state.to_csv(TABLES / "missing_components_by_state.csv", index=False)
    pd.DataFrame([metrics]).to_csv(TABLES / "summary_metrics.csv", index=False)

    geo_cols = [
        "GEOID", "stateabbr", "statedesc", "countyname", "countyfips",
        "totalpopulation", "depression_adjprev", "mhlth_adjprev", "access2_adjprev",
        "priority_score", "priority_decile", "priority_tier", "geometry",
    ]
    gdf[geo_cols].to_file(PROCESSED / "county_priority_scores.geojson", driver="GeoJSON")
    gdf[geo_cols].to_file(PROCESSED / "county_priority_scores.gpkg", layer="priority_scores", driver="GPKG")

    plot_map(gdf, FIGURES / "national_priority_map.png")
    plot_top(top, FIGURES / "highest_priority_counties.png")
    plot_scatter(ranked, FIGURES / "indicator_relationships.png")
    plot_preview(metrics, top, FIGURES / "portfolio_preview.png")

    qa = {
        "source_urls": {"cdc_places": PLACES_PAGE, "census_boundaries": CENSUS_ZIP},
        "source_sha256": {p.name: sha256(p) for p in raw_paths},
        "validation": {k: int(v) for k, v in validation.items()},
        "joined_counties": int(len(gdf)),
        "metrics": metrics,
        "analysis_note": "Percentile-average screening score; no causal interpretation.",
    }
    QA.parent.mkdir(parents=True, exist_ok=True)
    QA.write_text(json.dumps(qa, indent=2), encoding="utf-8")
    return qa


def main() -> None:
    places, census = acquire()
    ranked, validation, missing_by_state = clean_and_rank(places)
    gdf = build_geodata(ranked, census)
    qa = write_outputs(ranked, gdf, validation, missing_by_state, (places, census))
    print(json.dumps(qa["metrics"], indent=2))


if __name__ == "__main__":
    main()
