-- National percentile scoring for county-level planning signals.
-- The three inputs have different denominators, so this workflow ranks each
-- measure before combining them. Equal weighting is explicit and auditable.

WITH eligible AS (
    SELECT *
    FROM raw_places
    WHERE depression_adjprev IS NOT NULL
      AND mhlth_adjprev IS NOT NULL
      AND access2_adjprev IS NOT NULL
      AND totalpopulation > 0
),
scored AS (
    SELECT
        *,
        100 * percent_rank() OVER (ORDER BY depression_adjprev)
            AS depression_percentile,
        100 * percent_rank() OVER (ORDER BY mhlth_adjprev)
            AS distress_percentile,
        100 * percent_rank() OVER (ORDER BY access2_adjprev)
            AS uninsured_percentile
    FROM eligible
)
SELECT
    *,
    (depression_percentile + distress_percentile + uninsured_percentile) / 3.0
        AS priority_score
FROM scored
ORDER BY priority_score DESC, countyfips;
