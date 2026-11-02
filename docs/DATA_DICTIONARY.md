# Data dictionary

| Field | Meaning |
|---|---|
| `countyfips` | Five-character county FIPS code used for the spatial join. |
| `depression_adjprev` | CDC PLACES age-adjusted estimated prevalence of diagnosed depression among adults. |
| `mhlth_adjprev` | CDC PLACES age-adjusted estimated prevalence of frequent mental distress among adults. |
| `access2_adjprev` | CDC PLACES age-adjusted estimated prevalence of lacking health insurance among adults ages 18–64. |
| `depression_percentile` | National percentile rank of the depression estimate. |
| `distress_percentile` | National percentile rank of the frequent mental distress estimate. |
| `uninsured_percentile` | National percentile rank of the lack-of-insurance estimate. |
| `priority_score` | Equal-weight mean of the three percentile ranks. |
| `priority_decile` | Decile of `priority_score`; 10 is the highest signal group. |
| `priority_tier` | Plain-language grouping for screening and mapping. |

The component measures do not have identical denominators. The score is therefore a transparent rank-based planning aid, not a clinical scale.
