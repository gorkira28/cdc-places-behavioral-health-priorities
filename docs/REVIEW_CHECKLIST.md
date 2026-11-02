# Review checklist

## Key findings to verify

- 2,956 of 3,143 counties had complete values for all three components.
- 296 counties were in the highest composite-score decile.
- Those counties represented 8,023,198 residents.
- Depression and frequent mental distress estimates had Pearson r = 0.666.
- Tennessee had 83 highest-decile counties; West Virginia 34; Louisiana 31; Arkansas 29.

## Validation completed

- [x] Re-downloaded the official CDC and Census source files.
- [x] Recorded SHA-256 fingerprints in `outputs/qa_report.json`.
- [x] Confirmed 3,143 unique county FIPS keys in the source extract.
- [x] Confirmed prevalence inputs were within 0–100.
- [x] Required complete inputs for scoring.
- [x] Used a one-to-one county spatial join.
- [x] Ran three automated output tests successfully.
- [x] Visually inspected the portfolio preview and national map.
- [x] Checked that interpretation avoids causal and program-evaluation claims.

## Limitations requiring reviewer attention

- The composite is a transparent screening tool, not a validated index.
- 187 counties were excluded because the selected components were unavailable: all 120 Kentucky counties and 67 Pennsylvania counties.
- PLACES values are small-area model estimates.
- The insurance measure uses ages 18–64; the behavioral-health measures use adults.
- Population-weighted summaries remain summaries of county estimates, not survey-weighted national prevalence.

## Proposed GitHub metadata

- **Repository:** `cdc-places-behavioral-health-priorities`
- **Description:** `County behavioral-health prioritization using CDC PLACES, DuckDB SQL, Python and QGIS-ready GIS outputs.`
- **Homepage:** `https://gorkira28.github.io/#work`
- **Topics:** `behavioral-health`, `mental-health`, `cdc-places`, `public-health`, `epidemiology`, `healthcare-analytics`, `duckdb`, `sql`, `python`, `qgis`, `geospatial-analysis`, `data-quality`

## Proposed pinned-repository order after publication

1. `cdc-places-behavioral-health-priorities`
2. `nhanes-diabetes-ckd-awareness-gap`
3. `cms-nursing-home-staffing-quality-gap`
4. `type-2-diabetes-trial-results-reporting`
5. `pertussis-2025-surveillance-priorities`
6. `gorkira28.github.io`

This set shows Python, SAS, R, SQL and GIS across community health, survey analysis, healthcare quality, clinical research and surveillance. No pin settings were changed.

## Approval boundary

Nothing in this repository, the portfolio website or LinkedIn has been published by this run. GitHub and website publication require explicit approval. LinkedIn posting requires separate explicit approval.
