# Data

`raw/` is downloaded at runtime and excluded from version control. The workflow retrieves a selected-column extract from the CDC PLACES Socrata API and the U.S. Census Bureau 2025 county cartographic boundary file.

`processed/` contains recruiter-reviewable outputs:

- `county_priority_scores.csv`: analysis-ready county table.
- `county_priority_scores.geojson`: portable GIS layer.
- `county_priority_scores.gpkg`: QGIS-ready GeoPackage.

Run `python scripts/run_analysis.py` to rebuild all files. Source URLs, hashes and row-level QA are recorded in `outputs/qa_report.json`.
