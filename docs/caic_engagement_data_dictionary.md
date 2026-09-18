# CAIC Engagement Data — Data Dictionary

**File:** `data/processed/caic_engagement_by_year.csv`
**Coverage:** FY2015-16 through FY2024-25 (10 seasons)
**Purpose:** A participation/exposure proxy for Colorado avalanche fatalities. No
single published dataset of "backcountry users per year" exists (confirmed by
research — see project notes), so this table was hand-assembled from CAIC's own
annual report PDFs as the best available substitute: same organization, same
years, directly comparable to the CAIC fatality data we're already using.

This table was **not** downloaded from anywhere as a finished file. Every value
was manually transcribed from a specific page of a specific PDF. Six of the ten
PDFs were only recoverable via Wayback Machine snapshots after CAIC's old
`classic.avalanche.state.co.us` subdomain stopped reliably serving them. See
`source_pdfs.csv` for the exact source URL and retrieval method behind every row.

## Columns

| Column | Meaning |
|---|---|
| `fiscal_year` | CAIC's own fiscal-year label as printed on the report (e.g. `FY20-21`) |
| `avy_year` | Season-ending-year, matching the main accident dataset's `AvyYear` convention (a Nov 2020–Apr 2021 season = `2021`). Confirmed by cross-checking every `fatalities_reported` value against the accident database — all 10 years match exactly. Use this column, not `fiscal_year`, to join against the accident data. |
| `website_metric_type` | What the website number actually measures. **Not consistent across years** — see Caveat 1 below. |
| `website_metric_value` | The website number itself, in the units implied by `website_metric_type`. |
| `website_users` | Unique website users, only reported from FY20-21 onward. `NaN` for earlier years — this is a real gap, not a zero. |
| `website_metric_suspect` | `True` for exactly one row (FY16-17) — see Caveat 2. |
| `app_metric_type` | What the app number measures (downloads / active users / screen views). Also inconsistent — see Caveat 1. |
| `app_metric_value` | The app number, in the units implied by `app_metric_type`. |
| `app_users` | App active users where separately reported; `NaN` otherwise. |
| `fatalities_reported` | Fatality count as stated in that year's CAIC report text or chart. |
| `fatalities_source` | `report_text` for 9 of 10 years. `accident_database_backfill` for FY21-22, whose report never states a fatality count in prose — that value comes from our own accident dataset instead. |
| `source_pdf` | Filename of the source PDF (full URL + retrieval method in `source_pdfs.csv`). |
| `fatalities_accident_db` | Fatality count independently computed from the raw accident dataset, for cross-validation. |
| `fatalities_match` | `True`/`False` — whether `fatalities_reported` and `fatalities_accident_db` agree. All 10 rows are `True`. |

## Caveats — read before charting

**1. The metrics change definition mid-series.** This is the single most
important thing to understand before putting this on a dashboard.

- Website: `visits` (FY16-17) → `pageviews` (FY18-24) → `pageviews` + `users`
  reported together (FY21-25 only). A "visit" and a "pageview" are not the same
  statistic, and "users" (unique people) simply isn't available before FY21.
- App: `downloads` (FY16-19) → `active_users` (FY20) → `screen_views` + `users`
  (FY21, FY22, FY25) → not reported at all (FY23, FY24).

**Recommendation:** chart `website_metric_value` as a rough trend line with the
metric-type change called out visually (e.g. a shaded break or annotation at the
FY17→FY18 and FY20→FY21 boundaries), rather than implying it's one clean
apples-to-apples series. Treat `website_users` as its own short (FY21-25 only)
series if a cleaner comparison is needed.

**2. FY15-16 and FY16-17 report the identical website-visits figure —
1,732,675, to the digit** — while every other metric on those same two report
pages (app downloads, interviews given) differs between the two years. This
is almost certainly a copy-paste error in CAIC's own FY16-17 report template,
not a real coincidence. `website_metric_suspect = True` flags this row.
**Do not treat FY16-17's website number as reliable.** We don't know what the
real FY16-17 figure was — the honest move is to flag it, not guess a
replacement or quietly drop it.

**3. FY21-22 fatalities are backfilled, not report-stated.** That year's report
discusses the season narratively but never states a specific fatality count in
text or chart. The value used here (7) comes from summing our own accident
database for CO, `AvyYear == 2022` — flagged via `fatalities_source`.

**4. Every other year validates cleanly.** All 9 report-stated fatality counts
match the independently-computed accident-database counts exactly. That's a
real reliability signal for the underlying accident dataset, separate from the
engagement-metric caveats above.

**5. FY22-23's website figure was originally transcribed wrong — corrected
2026-09-13.** The value shipped in this table for months as `1,000,000`,
labeled `pageviews_rounded`. That was a plain transcription error, not a
rounding nuance: the actual report (page 6, "Growing Reach: Media Overview")
states **"3.1 Million Pageviews, ↑22%."** The 22% stat independently confirms
this — FY21-22's 2,527,632 × 1.22 ≈ 3,083,711, which lines up almost exactly
with the stated 3.1M. `website_metric_value` is now `3,100,000`, still typed
`pageviews_rounded` since the report itself only gives a one-decimal
headline figure rather than an exact count, unlike most other years.

This was caught by eyeballing the number against its neighbors on a chart —
it stood out as an implausibly large single-year dip (2.5M → 1M → 3M) — and
confirmed by fetching the original report PDF and reading the actual page.
Worth remembering as a general lesson: a number that looks wrong on a chart
is worth chasing back to its primary source before trusting a plausible-
sounding explanation (rounding) over a less comfortable one (data entry
error). The `caic_engagement_by_year.csv` value now correctly matches this
report; `build_caic_engagement.py` documents the correction inline.

**6. FY24-25's value (2,100,000) is also suspiciously round and hasn't been
double-checked against the source PDF.** Unlike FY22-23 (before the fix
above) it's labeled plain `pageviews`, not `pageviews_rounded`, so it may be
genuinely precise — but given Caveat 5 just turned up a real transcription
error at a similarly round number, this one deserves the same scrutiny
before being treated as exact. Source: `CAIC_FY25AnnualReport_Final_Web.pdf`.

## Citation

Colorado Avalanche Information Center, Annual Reports FY2015-16 through
FY2024-25. Compiled manually, October 2026.

**Note on `source_pdfs.csv` (rebuilt 2026-09-18):** the original per-row
citation file was lost before this project's files were fully backed up.
It was rebuilt from scratch by re-locating each of the 10 report PDFs and
re-verifying the fatality count and website/app numbers in each one against
this table, all 10 matched exactly. Nine of the ten (FY15-16 through
FY23-24) turned out to have a more durable public copy than the original
CAIC website or Wayback Machine: the Colorado State Publications Library's
permanent depository (`spl.cde.state.co.us`), which is what `source_pdfs.csv`
now cites for those years. FY24-25 isn't in that depository yet, so it's
cited directly from `avalanche.state.co.us`.

One thing that turned up during this re-verification, worth a look: the
FY21-22 report (`CAIC_FY22AnnualReport_Final_Small.pdf`) does appear to
state "seven people killed" directly in its text, which conflicts with this
table's `fatalities_source = accident_database_backfill` for that row. The
number itself (7) is correct either way, since it matches the independently
computed accident-database count, but the claim that it was backfilled
rather than report-stated may be a leftover error from the original
transcription. Worth a quick look at the actual report text before deciding
whether to correct `fatalities_source` for FY21-22.
