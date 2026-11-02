# LinkedIn post draft

## Post

2,956 U.S. counties had enough data to examine where behavioral-health need and insurance gaps may overlap.

For my latest public-health analytics project, I used the CDC PLACES 2025 release to study diagnosed depression, frequent mental distress and lack of health insurance.

I built the workflow with DuckDB SQL and Python, then joined the results to U.S. Census Bureau county boundaries for GIS analysis.

Depression and frequent mental distress moved together, with a county-level correlation of 0.67. Insurance gaps did not follow the same pattern everywhere.

I converted each measure to a national percentile and averaged the ranks into a transparent screening score. The highest decile included 296 counties representing about 8.0 million residents; Tennessee accounted for 83.

Kentucky and Pennsylvania lacked complete inputs, so their counties were excluded.

The ranking is a prompt for local review, not a verdict. CDC PLACES estimates are model-based and cannot evaluate local programs.

The repository includes reproducible acquisition, SQL scoring, automated QA checks, a QGIS-ready GeoPackage and publication-ready visuals.

Which additional factor would you test next: provider supply, rurality or transportation access?

#PublicHealth #HealthcareAnalytics

## First comment

Project repository: https://github.com/gorkira28/cdc-places-behavioral-health-priorities

## Publishing note

Suggested window: Tuesday–Thursday, 7:30–9:00 a.m. Central. The external link is kept in the first comment.
