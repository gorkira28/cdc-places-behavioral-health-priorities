# Portfolio case study: County Behavioral Health Priority Signals

## The question

Where do county-level estimates suggest that behavioral-health need and insurance barriers overlap strongly enough to justify a deeper local assessment?

## My approach

I built an end-to-end workflow using CDC PLACES 2025 estimates, DuckDB SQL, Python and U.S. Census Bureau county boundaries. Each county received national percentile ranks for diagnosed depression, frequent mental distress and lack of health insurance. I averaged those ranks into a transparent screening score, validated all keys and ranges, and exported both publication-ready charts and QGIS-ready spatial layers.

## The result

Among 2,956 counties with complete inputs, 296 formed the highest signal decile. The depression and frequent mental distress estimates were correlated at 0.67, but insurance gaps varied across counties with similar behavioral-health estimates. The top-decile counties represented about 8.0 million residents, providing a focused starting set for local capacity and access review.

## Why it matters

The useful product is not a list that declares which communities are “worst.” It is a reproducible triage tool that makes assumptions visible and tells analysts what evidence to gather next. The project explicitly separates screening from causal inference and program evaluation.

## Skills demonstrated

Python automation, DuckDB SQL, public API acquisition, complex data QA, percentile scoring, GIS joins, QGIS handoff, data visualization and careful public-health interpretation.
