# Methods

## Design

Cross-sectional, ecological analysis of county-level model-based estimates in the CDC PLACES 2025 release. The unit of analysis is the county or county equivalent.

## Measures

The project uses age-adjusted estimates for diagnosed depression, frequent mental distress and lack of health insurance. The insurance measure applies to adults ages 18–64; the behavioral-health measures apply to adults. Measures are ranked separately to avoid treating percentage-point differences across unlike denominators as directly additive.

## Priority score

DuckDB SQL calculates national percentile ranks for each component. The priority score is the unweighted mean of the three percentile ranks. Counties in the highest score decile are labeled the highest priority signal group. Equal weighting is a documented analytic choice, not a validated index.

## Spatial processing

County FIPS joins the CDC estimates to the U.S. Census Bureau 2025 1:500,000 county cartographic boundary file. The exported GeoJSON and GeoPackage retain the analysis fields for QGIS or other GIS software. The static map displays the contiguous United States for readability; the tabular and GIS outputs retain all matched geographies.

## QA/QC

- County FIPS must be unique and five characters.
- Prevalence inputs must be between 0 and 100.
- Complete cases are required for all three components.
- The spatial join is one-to-one.
- Raw file SHA-256 fingerprints are recorded.
- Automated tests verify keys, score bounds, source checks and output files.

All 120 Kentucky counties and 67 Pennsylvania counties lacked the three selected estimates in the source extract. They are excluded from scoring and appear white on the static map. State comparisons are therefore incomplete.

## Interpretation guardrails

PLACES values are small-area model estimates, not direct county survey estimates. CDC cautions that the model cannot detect effects of local interventions, so this project must not be used for program evaluation. Ecological rankings do not describe individual risk. The score identifies places for additional review; it does not prove unmet need or prescribe resource allocation by itself.
