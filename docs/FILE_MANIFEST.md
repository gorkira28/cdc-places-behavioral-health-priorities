# File manifest

## Root

- `.gitignore` — excludes raw data and local runtime files.
- `README.md` — recruiter-facing project narrative and run guide.
- `requirements.txt` — Python dependencies.
- `LICENSE` — MIT license for code.
- `CITATION.cff` — citation metadata.

## Analysis

- `scripts/run_analysis.py` — acquisition, cleaning, QA, analysis, spatial join and visualization.
- `sql/priority_scoring.sql` — DuckDB percentile-scoring query.
- `tests/test_outputs.py` — automated checks.

## Data and GIS

- `data/README.md` — provenance and rebuild notes.
- `data/processed/county_priority_scores.csv` — analysis table.
- `data/processed/county_priority_scores.geojson` — portable spatial layer.
- `data/processed/county_priority_scores.gpkg` — QGIS-ready layer.
- `gis/priority_score.qml` — reusable QGIS symbology.
- `gis/README.md` — QGIS loading instructions.

## Outputs

- `outputs/qa_report.json` — hashes, QA checks and headline metrics.
- `outputs/tables/highest_priority_counties.csv` — top-decile county details.
- `outputs/tables/highest_priority_counties_by_state.csv` — state summary.
- `outputs/tables/missing_components_by_state.csv` — geographic concentration of incomplete inputs.
- `outputs/tables/summary_metrics.csv` — one-row project metric table.
- `outputs/figures/portfolio_preview.png` — social and website preview.
- `outputs/figures/national_priority_map.png` — county choropleth.
- `outputs/figures/highest_priority_counties.png` — leading counties.
- `outputs/figures/indicator_relationships.png` — component relationship plot.

## Documentation

- `docs/DATA_DICTIONARY.md`
- `docs/METHODS.md`
- `docs/REFERENCES.md`
- `docs/PORTFOLIO_CASE_STUDY.md`
- `docs/LINKEDIN_POST_DRAFT.md`
- `docs/REVIEW_CHECKLIST.md`
- `docs/FILE_MANIFEST.md`
