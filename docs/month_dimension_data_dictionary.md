# DimMonth Data Dictionary

**File:** `data/processed/dim_month.csv`
**Built by:** `data/processed/build_month_dimension.py`
**Source:** `MM` column of `avalanche_fatalities_clean.csv` (12 distinct values, 1,016 rows, all mapped)

A lookup/dimension table, same pattern as `DimSeason` and `DimActivityCategory`.
Join `MM` to `avalanche_fatalities_clean[MM]` in Power BI to bring `MonthName`
and `SeasonMonthOrder` onto any Q3 (seasonality) visual.

## Why this exists

`MM` is a plain calendar month (1 = January ... 12 = December), but an
avalanche season runs November through the following October, not January
through December. Charting `Total Fatalities` by `MM` with the default sort
(1, 2, 3...) would split the winter season across both ends of the axis —
November and December would land at the far right, after April and May,
even though they're the *start* of the season a viewer actually cares about.

This is the same category of bug as the `SeasonLabel` and `Decade` sort
issues hit earlier in the project — just for months instead of
seasons/decades. Unlike those two, though, this one is fully mechanical, not
a judgment call: there's no ambiguity about what season-order position March
occupies, so this table has no caveats section the way `DimActivityCategory`
does.

## Columns

| Column | Meaning |
|---|---|
| `MM` | The raw CAIC value (1–12), unchanged — the join key back to the fact table. |
| `MonthName` | Full month name (`"November"`, etc.), for axis/legend labels. |
| `SeasonMonthOrder` | 1–12, season order starting at November. Use this (not `MM`) to sort any chart with month on an axis. |

## Row counts by month (season order)

| Month | Rows |
|---|---|
| November | 43 |
| December | 135 |
| January | 224 |
| February | **245** |
| March | 190 |
| April | 102 |
| May | 34 |
| June | 25 |
| July | 5 |
| August | 5 |
| September | 1 |
| October | 7 |

February is the single deadliest month nationally (245 rows), with
January and March close behind — consistent with peak backcountry travel
overlapping peak/persistent-weak-layer avalanche danger in the Rockies and
similar ranges. The June–September tail (36 rows) is almost entirely
Climbers in Alaska/Washington/Colorado — high-alpine glacier and snowfield
avalanches, a real summer-mountaineering hazard, not noise (see
`fact_table_data_dictionary.md` if a caveat on this gets added later).

## Rebuilding this table

Deterministic and unlikely to ever need a rebuild — the only way it could
break is if a new `MM` value outside 1–12 showed up in a future CAIC export,
which `build_month_dimension.py` will catch and error on rather than
silently mis-map.
