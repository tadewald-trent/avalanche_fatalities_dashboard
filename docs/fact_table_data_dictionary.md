# FactAvalancheEvents Data Dictionary

**File:** `data/processed/avalanche_fatalities_clean.csv`
**Built by:** `data/processed/build_clean_fact_table.py`
**Source:** `data/raw/CAIC_Accident_Data_Oct_2025.xlsx` ("Data" sheet), 1,016 rows, 1951-2025

All 14 original columns are preserved unchanged. 11 columns are added below —
each one documents what it is, how confident we are in it, and why it lives in
Python rather than being computed inside Power Query (see project notes for
the full Python-vs-Power-Query rationale).

## Added columns

| Column | Confidence | What it is |
|---|---|---|
| `HasLocation` | Confirmed | `False` where `lat`/`lon` are the (0,0) placeholder rather than a real missing value. 100% of pre-2010 rows, 0% of 2020s rows — era-driven, not random. Use to filter map visuals; do not plot rows where this is `False`. |
| `HasDescription` | Confirmed | `False` where `Description` is null. 74% of all rows. Sharper than "pre-2010": of the 265 rows with a description, 264 are 2013-2025 and exactly 1 is from 1986 — the field is effectively a modern-era-only field starting AvyYear 2013, not a gradually-improving one. Treat any description-derived analysis as a 2013-2025 window (13 seasons), and treat the 1986 row as a one-off outlier worth excluding from that window rather than folding in. |
| `SettingCode` | Confirmed | `Setting` with the one-off `"-closed terrain"` suffix stripped out, so `"SA"` and `"SA-closed terrain"` become the same code. |
| `IsClosedTerrain` | Confirmed | `True` for the 2 rows that were `"SA-closed terrain"` — closed-terrain incidents kept as their own flag instead of silently merged into `"SA"`. |
| `SettingLabel` | **Confirmed by CAIC** | Decode of `BC`/`SA`/`TN`/`RD`/`RS`/`MN`, confirmed directly by Spencer Logan (CAIC) via email reply, 2026-08-25: `BC`=Backcountry, `SA`=Ski Area, `TN`=Town/Urban, `RD`=Road, `RS`=Railroad, `MN`=Mine. `SA-closed terrain` folds into `SA` per his guidance, distinguished instead by the `IsClosedTerrain` flag above. Two of our original inferred guesses were wrong before this reply (`TN` was guessed as "Transportation Corridor," `RS` as "Residence") — kept in the script's comments as a reminder of why unconfirmed labels were never presented as fact in the interim. See the data-quality caveat below before using this field (or any categorical field) in cross-state or long-term trend analysis. |
| `MentionsInjured` | Confirmed | `True` if `Description` contains "injured". Simple substring match — reliable, since the field turns out to be a formulaic incident summary, not free narrative (verified by reading all 265 non-null descriptions before writing any extraction logic). |
| `MentionsCriticalBurial` | Confirmed | `True` if `Description` mentions "critical" — CAIC's own term for an airway-compromised partial burial, a real severity tier distinct from an ordinary partial or full burial. |
| `AlternateCause` | Confirmed | `standard_burial` / `cornice_collapse` / `serac_fall`, only set where `HasDescription` is `True`. 5 of 265 described events are not ordinary snow burials — 4 cornice collapses, 1 serac fall. Worth its own note on the human-factors panel: not every death here is "buried by an avalanche" in the usual sense. |
| `PeopleCaught` | Best-effort, 99% parse rate | Regex-extracted from the leading "N [activity] caught..." clause. Handles both digits and spelled-out numbers (`"One snowmobiler..."`). Null where extraction failed or was invalidated. |
| `PeopleCaughtParsed` | Confirmed | `True`/`False` flag for whether `PeopleCaught` is trustworthy. **262 of 265** description rows parsed successfully. 3 did not: 2 rows say `"Multiple..."` with no number given (genuinely unknown, left null rather than guessed), and 1 row — `"1 skier and 1 snowmobiler killed"` — initially mis-parsed as 1 person caught when the real count was 2, caught by a sanity check (parsed count can never be less than `Killed`) and invalidated rather than shipped. |
| `PeopleInjured` | Best-effort | Regex-extracted "N injured" count. Null where not mentioned or not a parseable number. |

### Pitfall: a "people caught per person killed" ratio must filter both sides the same way

Building the Q2 modern-era panel (2026-09-15), a first pass at a
`PeopleCaught` / `Killed` ratio by `ActivityCategory` produced an impossible
result — Inbounds came out to 0.78, i.e. fewer people caught than killed,
which cannot happen (you can't kill more people than were caught in the same
avalanche; this is the same invariant `PeopleCaughtParsed`'s own sanity
check relies on). Root cause: the numerator (`SUM(PeopleCaught)`) silently
excludes rows where `PeopleCaughtParsed` is `False`, since `PeopleCaught` is
null there — but the denominator (`SUM(Killed)`) doesn't, so a row like the
2020 Inbounds event ("Multiple skiers caught... 3 killed", unparseable
count, correctly left null) contributes 3 to the denominator and 0 to the
numerator, dragging the ratio below 1.

**Fix:** filter `Killed` by `PeopleCaughtParsed = TRUE` too, so both sides of
the ratio are computed over the exact same set of rows. In DAX:

```
Caught Per Killed (Modern Era) =
DIVIDE(
    CALCULATE(
        SUM(avalanche_fatalities_clean[PeopleCaught]),
        avalanche_fatalities_clean[PeopleCaughtParsed] = TRUE,
        avalanche_fatalities_clean[AvyYear] >= 2013
    ),
    CALCULATE(
        SUM(avalanche_fatalities_clean[Killed]),
        avalanche_fatalities_clean[PeopleCaughtParsed] = TRUE,
        avalanche_fatalities_clean[AvyYear] >= 2013
    )
)
```

General lesson, same one `PeopleCaughtParsed`'s original sanity check
taught: any ratio built from a best-effort/partially-null field needs its
denominator restricted to the same subset as the numerator, not just "all
rows in scope." Worth checking for next time a rate or ratio measure gets
built from any of the best-effort columns in this table.

### Pitfall: check a column's *imported* data type, not just its source type

Building the Q4 severity table (2026-09-15), a measure that filtered on
`AvyYear >= 2013` threw: *"DAX comparison operations do not support
comparing values of type Text with values of type Integer."* The formula
was correct and fully table-qualified — the actual problem was that
`AvyYear` had been imported into Power BI as a **Text** column instead of
Whole Number. CSV has no native numeric type, so Power BI has to infer each
column's type from what it sees on import, and it inferred wrong for this
one. This had been sitting in the model invisibly the whole project,
because no existing chart before Q4 did a raw row-level numeric comparison
against `AvyYear` directly (`Decade`, `SeasonLabel`, and the modern-era
measures that came before this one all went through other fields or
aggregate measures instead).

**Fix:** in Power BI's Data view, select the column and change its Data
type from Text to Whole Number directly (Column tools → Data type) — a
mechanical, no-judgment-call fix, same category as the `Region` and
`FatalityGroupSize` columns, so it's done in Power BI rather than round-
tripped through Python.

**General lesson:** a column's *logical* type (an integer year, in this
case) and its *imported* type in Power BI are two different things, and
they can silently disagree — the CSV export doesn't carry type information,
so Power BI's auto-detection is a guess, not a guarantee. Worth a quick
Data-type check (Column tools ribbon) on any column the moment a measure
starts doing direct comparisons or arithmetic on it for the first time,
rather than assuming a column that "looks like a number" was actually
imported as one.

### Pitfall: a measure that "should" be 0 can silently evaluate to blank

Building the Q5 record-keeping-coverage chart (2026-09-16), `% HasLocation`
and `% HasDescription` — both simple `DIVIDE(CALCULATE(COUNTROWS(...),
condition), COUNTROWS(...))` measures — caused 5 of 8 decades to vanish
entirely from a table and a line chart. The formulas were correct DAX and,
read purely as math, `DIVIDE(0, 106)` (zero matching rows out of 106 in a
decade) is unambiguously `0.0`, not blank — `DIVIDE` only substitutes a
blank/alternate result when the *denominator* is zero, and `COUNTROWS`
itself never returns blank, even for an empty filtered table.

**Root cause:** Power BI's visual query engine (`SUMMARIZECOLUMNS`, which
is what a Table or Chart visual actually runs under the hood) has a known
behavior where a `CALCULATE` filter on a column from the *same table* as
the visual's grouping column (here, `Decade` and `HasLocation` are both on
`avalanche_fatalities_clean`) can cause a zero-row match to collapse into
`BLANK()` rather than surface as a literal `0` — an engine-level
optimization quirk, not a bug in the formula itself. Since a Table/Chart
visual drops a category entirely when *every* measure in it is blank for
that category, decades where both `%` measures happened to be exactly 0%
disappeared completely, while decades where at least one measure was
non-zero (e.g. 1980s had a nonzero `% HasDescription` from the single 1986
outlier row) survived with the other cell just blank.

**Fix:** append `+ 0` to the end of the `DIVIDE(...)`. In DAX,
`BLANK() + 0` evaluates to `0`, which is enough to stop the engine from
treating the result as absent:

```
% HasLocation = 
DIVIDE(
    CALCULATE(COUNTROWS(avalanche_fatalities_clean), avalanche_fatalities_clean[HasLocation] = TRUE),
    COUNTROWS(avalanche_fatalities_clean)
) + 0
```

**General lesson:** "the chart renders without an error" is not the same
as "the chart is showing every category it should." A clean-looking curve
with no error banner can still be silently missing data — caught here only
by cross-checking the rendered categories against a Python-computed
reference table and noticing four decades simply weren't on the axis. Same
instinct as the `PeopleCaughtParsed` and `AvyYear` pitfalls above: verify
the actual numbers/categories, don't just trust that "it rendered" means
"it's right."

## Data-quality caveat from CAIC (Spencer Logan, 2026-08-25)

When confirming the `Setting` codes, Spencer added an unprompted but important
note: `Setting` and other categorical fields in this dataset reflect **each
individual investigator's best judgment at the time**, not a standardized
taxonomy applied consistently. Reports have been compiled by different people
across the decades this dataset spans, and — critically — **incidents outside
Colorado were not investigated by CAIC staff at all**, only compiled by them
from other sources.

Practical implications for this project:
- Long-term trend lines (e.g. "has Setting X grown as a share of fatalities
  over time") may partly reflect changing investigator conventions, not just
  changing reality on the ground.
- The "National with a Colorado spotlight" framing of this dashboard is
  partly a response to this caveat — Colorado's own CAIC-investigated rows
  are the most internally consistent subset of the data, which is worth
  surfacing explicitly on the dashboard rather than treating all 1,016 rows
  as uniformly reliable.
- This caveat applies to any categorical field carried over from the raw
  data (`Setting`, `PrimaryActivity`, `TravelMode`), not just the ones this
  script enriches.

This note should appear somewhere visible on the finished dashboard (e.g. a
methodology/caveats panel), not just here in the docs.

## AvyYear 2025 is CAIC's own designated "current year" — treat as provisional

The raw workbook (`CAIC_Accident_Data_Oct_2025.xlsx`, "By Month" sheet) labels
its 2025 column **"2025 <-Current Year"**, distinct from every year before
it. That's not an inference — it's CAIC's own built-in flag, meaning as of
this file's October 2025 export, the 2024-25 season was still being treated
as open/in-progress, not a closed, finalized historical year the way 1951-
2024 are.

Practical implication: any total, chart, or comparison that includes AvyYear
2025 (`2024-25` on season-labeled visuals) should be treated as provisional,
not final — investigation and reporting for the most recent season can lag
behind the season itself, and a low count there (e.g. CO Fatalities = 3 in
2024-25 vs. 11 the season before) may partly reflect incomplete reporting at
export time rather than a genuinely quieter season. This affects:
- Page 1's decade bar chart — the 2020s bucket is already flagged as partial
  for having fewer seasons; this is a second, independent reason 2025
  specifically shouldn't be read as a finalized data point.
- Page 2's CO-vs-engagement panel, and any future visual using the most
  recent season.

Don't drop 2025 from the data — it's real, it's just not necessarily
complete. Flag it wherever it appears rather than pretending it carries the
same certainty as older, closed-out seasons.

## Why the sanity check matters

The `PeopleCaughtParsed` invalidation above isn't a hypothetical — it's a real
bug the script caught on its own before this data ever reached a chart. The
rule is mechanical and just three lines of code: parsed `PeopleCaught` can
never be less than `Killed`, because you cannot kill more people than were
caught in the same avalanche. One row violated it on the first run, got
printed to the console with its full text so it could be inspected by eye,
and was invalidated rather than silently kept wrong. Re-running the script
reproduces this exact check every time — if a future edit to the regex ever
reintroduces a similar bug, the script will say so immediately instead of
letting a wrong number ride into Power BI.
