# Research Questions — Colorado Avalanche Fatalities Dashboard

This is the working definition of what this dashboard is trying to answer.
Every report page should trace back to one of these five questions. When a
visual doesn't obviously serve one of them, that's a signal to cut it or
fold it into one that does discipline matters more here than volume of
charts.

Source data: CAIC accident database, 1,016 fatal events, 1951-2025 (see
`fact_table_data_dictionary.md`), and the hand-assembled CAIC engagement
proxy, FY2015-16 through FY2024-25 (see `caic_engagement_data_dictionary.md`).

One page — **Data Quality and Methodology** — is deliberately not one of the
five numbered questions below. Its job is to qualify all five, not answer
one of them, so it lives as an appendix at the end of this document instead
of taking a Q-number.

---

## Q1. National trend

**Question:** How have avalanche fatalities changed nationally over the
last 75 seasons?

**Why it matters:** A rising death count on its own is ambiguous — it could
mean the activity is getting more dangerous, or it could just mean more
people are doing it. Tremper's core argument is that avalanche risk is
mostly a human-factors problem, not a snowpack problem; a naive "deaths are
up" headline without an exposure denominator plays directly into the wrong
conclusion. This page can only show the raw national trend — the actual
exposure-denominator comparison, using CAIC's own engagement data as a
Colorado-specific proxy, lives entirely on Q5.

**Supports it:** `Total Fatalities`, `Fatalities 5yr Avg`, `Avg Fatalities
Per Season`, `Deadliest Season Fatalities`/`Label`, `Decade` (all built).

**Status: Done.** Built as a single national-trend page (`Q1`): a `Total
Fatalities` by `Decade` bar chart, a KPI card (`Avg Fatalities Per
Season`), a `Deadliest Season Label`/`Fatalities` table, and a `Total
Fatalities` + `Fatalities 5yr Avg` line chart by `SeasonLabel`. Two named
findings, verified against the fact table before writing up (per-season
`Killed` sums by decade): (1) the headline trend — fatalities rose sharply
from the 1950s through the 1990s (about 4 to 22 per season, a 5x increase),
then flattened; the three most recent decades all sit in a narrow 24-28-
per-season band rather than continuing to climb, and the modern era
(2000s-2020s) still averages roughly 3.6x the earliest three decades
(1950s-1970s), almost entirely from pre-2000 growth; (2) the COVID-era
2020-21 season is the deadliest on record (37 fatalities, more than double
the historical average), plausibly driven by a surge of inexperienced
backcountry users during the pandemic — a Q2 (human-factors) story
surfacing on the Q1 page (see "How these connect").

**Scoping decision:** Colorado was originally meant to get its own
spotlight on this page — comparing Colorado fatalities against CAIC's
website-engagement data as an exposure proxy, hence the page's original
"National trend, with a Colorado spotlight" framing. Two things changed
that: (1) the chart didn't fit on Page 1, so it got built as a second tab
(`Q1 pt2`) instead of living here; (2) once the project's original
motivating question — does more readiness engagement track with fewer
fatalities — got its own proper treatment as Q5, with the readiness-proxy
framing, verified stats, and full findings/caveats text, `Q1 pt2` became a
straight duplicate of Q5's chart and was deleted. Q1 is now purely the
national trend, with no Colorado-specific visuals of its own; the
Colorado-vs-engagement comparison lives entirely on Q5.

**Caveats to carry onto the page:** the 1950s (9 seasons) and 2020s (6
seasons, through 2025) bars on the by-decade chart are partial decades —
their totals aren't directly comparable to the other, complete decades, and
2025 itself should be read as a partial, provisional season. Record-keeping
also improved over time (see the Data Quality appendix — narrative/location
detail only becomes reliable starting in the 2000s-2010s), so part of the
long-run rise may reflect better documentation rather than a purely real
increase in fatalities, on top of the genuine effect of more people going
into the backcountry — which this page can't separate out either (that's
why Q5 exists).

---

## Q2. Human factors and the modern-era activity breakdown

**Question:** What activities are most associated with fatal accidents, and
has that mix changed over the 75-year history of the data?

**Why it matters:** This is the most direct line to Tremper's "it's not the
avalanche, it's the decision" framing — activity type and access mode are
pieces of the story that are actually within a person's control, unlike
snowpack conditions.

**Supports it:** `DimActivityCategory` (built from raw `PrimaryActivity`,
24 values collapsed into 6 categories), `Decade`/`AvyYear`.

**Status: Done.** Built as a two-chart page (`Q2`): a category breakdown
(`Total Fatalities` by `ActivityCategory`) and a 100%-stacked composition
chart by `Decade`, with a named finding — the collapse of occupational/
passive exposure (55%→under 10% since the 2000s) and the rise of motorized
backcountry recreation (0%→over 40% by the 2000s, tracking the real
snowmobile-access boom) are the two biggest structural shifts in who
avalanches kill. Both charts checked against `PrimaryActivity`'s full
75-year coverage (zero missing values in any decade) and pass a face-
validity check against known avalanche-sport history.

**Scoping decision, 2026-09-15:** a third piece was designed but
deliberately cut — a "modern-era circumstances" panel using
`MentionsInjured`, `MentionsCriticalBurial`, `AlternateCause`, and a
"people caught per person killed" ratio from `PeopleCaught`/
`PeopleCaughtParsed`. These fields only exist for 2013-2025 (`Description`
is a single 1986 outlier, then nothing until 2013 — see
`fact_table_data_dictionary.md`), and 4 of the 6 activity categories have
single-digit-to-teens sample sizes in that window. It would have extended
Q2 into the "circumstances" half of the question (group exposure, incident
severity), but on meaningfully weaker evidence than the two charts already
built. Cut in favor of keeping Q2 resting on its strongest material rather
than diluting it with a thin, exploratory add-on — not because the idea was
wrong, just lower priority than the rest of the project's scope. Worth
revisiting later if there's time, but not a gap that needs filling before
this page is considered done.

**Caveats carried onto the page:** activity categories are an analytical
judgment call, not a CAIC-defined taxonomy (see
`activity_category_data_dictionary.md`); categorical fields like
`PrimaryActivity` reflect individual investigator judgment, not a
standardized taxonomy applied consistently across 75 years (Spencer Logan,
CAIC) — an apparent shift in mix may partly reflect changing investigator
conventions, not just changing conditions on the mountain; the
"Occupational, Passive & Other" category is a deliberate grab-bag and its
position on the (value-sorted) composition chart reflects size, not
coherence.

---

## Q3. Seasonality and geography, Colorado in national context

**Question:** When (month/season timing) and where (setting: backcountry,
ski area, road, etc.) do fatal accidents cluster, and how does Colorado's
distribution compare to the national one?

**Why it matters:** There are two separate reasons to look at Colorado on
its own here, not just one, and they're worth keeping distinct:

1. **A real scientific reason to expect a genuine difference.** Colorado is
   widely known in avalanche science for having one of the most dangerous
   snowpacks in the world — its continental (cold, dry) snowpack develops
   persistent weak layers early in the season (faceted grains/depth hoar)
   that can linger and produce deep slab instability all winter, unlike
   maritime snowpacks (e.g. the Cascades, Sierra Nevada) that tend to
   stabilize faster. Tremper's book covers this distinction directly. That's
   an independent reason to *expect* Colorado's when/where pattern to
   genuinely differ from the national one — not just a data artifact to
   correct for.
2. **A data-quality reason to trust Colorado's numbers more.** This is where
   the CAIC Setting-code confirmation and Spencer Logan's investigator-
   subjectivity caveat matter most directly — this question is explicitly a
   cross-region, cross-era comparison, which is exactly the kind of
   comparison he warned is weakest in this dataset. Colorado's rows are the
   most internally consistent subset (CAIC staff investigated them directly;
   other states' incidents were only compiled from other sources).

Put together: we have a real scientific reason to *expect* Colorado to look
different, and a real methodological reason to *trust* Colorado's numbers
more than the rest of the dataset's — which is exactly why this page
compares Colorado against the rest of the nation side by side rather than
blending all 1,016 rows into one national answer.

**Supports it:** `SettingLabel`, `IsClosedTerrain`, `HasLocation`,
`Region` (Colorado vs. Rest of Nation, State-derived), `DimMonth`
(`MonthName`/`SeasonMonthOrder`, built to fix calendar-vs-season month
ordering).

**Status: Done.** Built as a two-chart page (`Q3`): a normalized timing
chart (`% of Region Total` by `MonthName`, season-ordered via `DimMonth`,
split by `Region`) and a 100%-stacked `SettingLabel` breakdown by `Region`.
Two named findings: (1) both regions peak Feb-March, but Colorado's season
runs hotter into March (20.7% of its total vs. 17.0% nationally) while the
rest of the nation has a longer late-spring tail (May-June: 9.6% vs. 2.4%),
likely reflecting high-elevation glaciated terrain in Alaska/Washington
(ties back to the summer-fatalities-are-almost-all-Climbers finding from
`fact_table_data_dictionary.md`); (2) Road incidents are roughly 3x
Colorado's share of the rest of the nation's (5.2% vs. 1.8%), plausibly its
mountain highway corridors, though this rests on a modest count (17 either
way) and shouldn't be overstated. `Region` built as a one-line DAX
calculated column (`IF(State = "CO", "Colorado", "Rest of Nation")`), not a
Python script, since there's no judgment call in a binary State split —
deliberate contrast with `DimMonth`, which did get the full script
treatment since its content (a 12-row mapping) actually needed validating.

**Caveats to carry onto the page:** Setting and other categorical fields
reflect individual investigator judgment, not a standardized taxonomy, and
incidents outside Colorado were compiled by CAIC, not investigated by CAIC
staff. This is the page where that limitation is most likely to distort a
finding if it isn't surfaced — Colorado's own rows are the most internally
consistent subset of the data and should be called out as such. At the same
time, don't let that caveat get read as "so any CO/rest-of-nation
difference is probably just noise" — Colorado's snowpack really is
different, so a real difference showing up on this page would be
consistent with established avalanche science, not just something to
explain away.

---

## Q4. Multi-fatality group events

**Question:** How often does a single avalanche kill more than one person,
and what distinguishes those group-loss events from single-fatality ones?

**Why it matters:** Group decision-making (not individual risk-taking) is
its own distinct human-factors story — a group of experienced people can
still make a catastrophic collective decision (groupthink, one person
triggering a slide that catches several others).

**Supports it:** `Killed`, `PeopleCaught`/`PeopleCaughtParsed`,
`FatalityGroupSize` (built from `Killed`), `ActivityCategory`.

**Status: Done.** Built as a page (`Q4`) with two KPI cards, a
`% Multi-Fatality Events` bar chart by `ActivityCategory`, and a severity-
comparison table (`FatalityGroupSize` rows vs. `Modern Parsed Events`,
`Avg People Caught (Modern)`, `Avg Killed (Modern, Parsed)`,
`Survival Rate (Modern)`). Two named findings: (1) multi-fatality events are
16% of all 1,016 fatal accidents but 32% of all deaths, and the danger
compounds once caught — modern-era (2013-2025) survival rate for people
caught in a multi-fatality event is 24%, versus 32% for single-fatality
events (261 modern, parsed events); (2) Climbing/Mountaineering has by far
the highest multi-fatality rate of any activity category (37.5%, versus
11-20% for every other category), plausibly reflecting roped travel and
shared route exposure — a single avalanche can catch an entire climbing
party, a structurally different exposure pattern than solo or small-group
backcountry/snowmobile travel. `FatalityGroupSize` built as a one-line DAX
calculated column off `Killed` (relabeled `Single-fatality (1)` /
`Multi-Fatality (2+)`) — purely mechanical, no Python script needed, same
rationale as `Region` in Q3.

**Build note:** the `AvyYear` column was imported into Power BI with the
wrong data type (Text instead of Whole Number) — invisible until a measure
actually did a numeric comparison against it (`AvyYear >= 2013`), which
threw a "DAX comparison operations do not support comparing values of type
Text with values of type Integer" error. Existing charts never hit this
because none of them did a raw row-level numeric comparison against
`AvyYear` directly. Fixed by changing the column's Data type to Whole
Number directly in Power BI's Data view (mechanical fix, no Python needed).
Worth remembering for any future measure that filters on `AvyYear` a new
way — see `fact_table_data_dictionary.md` for the full writeup.

**Caveats to carry onto the page:** the severity-comparison table is
restricted to the 261 modern-era (2013-2025) events with both a description
and a valid `PeopleCaught` parse — only 27 of those are multi-fatality, a
small sample that should be read directionally, not as a precise rate. The
activity-category breakdown carries the same investigator-subjectivity
caveat as Q2 and Q3: `PrimaryActivity` reflects individual investigator
judgment, not a standardized taxonomy applied consistently across 75 years.

---

## Q5. Backcountry readiness engagement vs. Colorado fatalities

**Question:** Does CAIC website engagement — used here as a proxy for how
many people are preparing before heading into the backcountry, not a
headcount of participants — show a rising trend over FY2015-16 through
FY2024-25, and do Colorado avalanche fatalities show any corresponding
trend against it?

**Why it matters:** This is the question that started the whole project:
is backcountry travel actually becoming safer as gear, forecasting tools,
and avalanche education have improved? Added mid-project, once it was clear
the other four questions wouldn't get to it on their own. Research turned
up no clean, continuous, publicly available time series of backcountry
participation or safety-equipment/education adoption — what exists is
scattered industry press-release snapshots (SIA/SFIA) with inconsistent
year-to-year definitions, and even peer-reviewed research using CAIC's own
accident data (Niemann et al., 2022) had to drop an avalanche-education
variable entirely due to 78% missing data. CAIC's own website/app
engagement numbers are the best available substitute: same organization,
same years, directly comparable to the fatality data already on this
dashboard, and tied to Tremper's "check the forecast before you go"
risk-reduction framing already central to this project's citations.

**Supports it:** `caic_engagement_by_year` (`Website Value Clean`
measure), `fatalities_accident_db` (Colorado fatality count, cross-
validated against the main accident database).

**Status: Done.** Built as a page with a dual-axis combo chart: engagement
(`Website Value Clean`, columns) against Colorado avalanche fatalities
(line, secondary axis) by `avy_year`. Recomputed independently in Python
against the canonical CSV before documenting (project convention — see Q4
and the appendix for the same cross-check habit) — and this cross-check
caught a real error in an earlier draft of this write-up, worth recording
as its own small lesson: engagement has a real upward trend against year
(r≈0.57, excluding the flagged FY16-17 value), rising roughly 40% comparing
the first three valid years' average (FY15-16–FY18-19, ≈1.95M) to the most
recent three (FY22-23–FY24-25, ≈2.74M). Fatalities show almost no
relationship to year over the same span (r≈0.16) — an earlier pass at this
number wrongly excluded FY16-17 from the *fatalities* series too (that
year's fatality count isn't suspect, only its website figure is), which
artificially flattened the correlation to r≈-0.03. Keeping all 10 years for
fatalities and only excluding the flagged year from the engagement series
gives the correct r≈0.16 — still a weak relationship, still governed mostly
by each season's snowpack rather than by engagement's rise, just not quite
as flat as the earlier miscalculation suggested.

**Finding, as written on the page:** "Website engagement and Colorado
fatalities move largely independently of each other over this decade.
Engagement has a real upward relationship with time (moderate positive
correlation, r ≈ 0.57, excluding the flagged FY16-17 value): roughly 40%
higher in the most recent three years than the first three. Fatalities
show almost no relationship to time at all (r ≈ 0.16), bouncing up and
down mainly with how dangerous each season's snowpack was rather than
tracking engagement. That pattern fits with the idea that as more people
prepare for backcountry trips, risk per person is going down, even though
we can't say for sure why — better gear, more education, and more
cautious decisions could all be playing a part."

**Build note:** the duplicate FY16-17 website figure (see
`caic_engagement_data_dictionary.md` Caveat 2) needed the same
flag-don't-guess treatment used everywhere else in this project. Built as
a `Website Value Clean` measure — `IF(website_metric_suspect = TRUE,
BLANK(), website_metric_value)` — so the suspect year renders as a real
gap on the chart rather than either the fake duplicate value or a
fabricated substitute. Confirmed values match the source CSV exactly.

**Caveats, as written on the page:** "This measures engagement with CAIC's
safety information, not a literal participant headcount — it can't
distinguish one person checking daily from many people checking once, and
some traffic is likely storm- or news-driven rather than trip planning.
The metric itself changes definition mid-series (website traffic switched
from 'visits' to 'pageviews' between FY17 and FY18, not directly
comparable), and the 2017 gap in the chart is a known duplicate value in
CAIC's own report rather than missing data. FY21-22's fatality count is
backfilled rather than report-stated, and 10 seasons is enough to see a
direction, not enough to prove one. A peer-reviewed 2022 study using
CAIC's own fatality data tried to track avalanche-education trends over a
similar window and had to drop the analysis entirely — 78% of the
underlying reports didn't record it."

**Naming note:** this page is labeled `Q5` in Power BI. The page previously
documented here as Q5 (`Data Quality and Methodology`) has moved to an
appendix at the end of this document — it was never actually a
findings-bearing research question, it's a page that qualifies all of
them, so it doesn't need a Q-number of its own.

---

## How these connect (worth remembering as you build)

Findings don't stay inside their own question. The 2020-21 deadliest-season
finding surfaced on the Q1 page, but it's really a Q2 (human factors) story
— a surge of inexperienced backcountry users during COVID — wearing Q1's
clothes. Expect more of this. When it happens, it's worth a cross-reference
rather than pretending each page is hermetically sealed from the others.

---

## Appendix: Data Quality and Methodology (not a findings page — an honesty page)

Not one of the five numbered research questions above — this page's job is
to qualify all five of them, not answer one of them, so it's documented
here rather than taking a Q-number.

**Question:** How has the record-keeping itself changed over 75 years, and
what does that mean for how much weight any of the above findings can
actually bear?

**Why it matters:** Every numbered question on this dashboard is gated by
this one. A viewer who only sees the pretty trend lines and never sees this
page could walk away trusting comparisons the data can't actually support.

**Supports it:** `HasLocation`, `HasDescription` over time, the Setting
confirmation and investigator-subjectivity caveat (see
`fact_table_data_dictionary.md`), the engagement-metric-definition-change
caveat (see `caic_engagement_data_dictionary.md`).

**Status: Done.** Built as a page (`Data Quality and Methodology`) with a
single centerpiece chart (`% HasLocation` and `% HasDescription` by
`Decade`) and four caveat text boxes. The chart tells the "record-keeping
changed over 75 years" story on its own: both fields sit at 0% through the
1950s-1990s, `% HasLocation` climbs starting in the 2000s (19.8%, then
84.4% by the 2010s), `% HasDescription` only starts climbing a decade later
(63.8% in the 2010s), and both reach 100% by the 2020s. The four caveats
carried onto the page: (1) investigator judgment — `Setting`,
`PrimaryActivity`, and other categorical fields reflect individual
investigators' judgment, not a standardized taxonomy (Spencer Logan, CAIC);
(2) Colorado vs. rest of nation — Colorado's rows were investigated
directly by CAIC staff, other states' only compiled from other sources,
making Colorado the most internally consistent subset (ties directly to
Q3's framing); (3) the CAIC engagement metric used on Q5 changes its own
definition mid-series and carries a suspected duplicate (FY16-17) and a
backfilled value (FY21-22); (4) `AvyYear` 2025 is CAIC's own flagged
"Current Year" as of this export and should be read as provisional, not a
finalized season.

**Build note:** building the coverage chart surfaced a second real DAX
lesson (the first being the `AvyYear` Text-import bug from Q4). A `DIVIDE`
measure that should mathematically evaluate to `0` for a decade with zero
matching rows (e.g. `% HasLocation` in the 1950s) instead evaluated to
**blank**, which caused Power BI's table/line-chart visuals to silently
drop that decade's entire row/category — five of eight decades vanished
from the chart until this was caught. Root cause: Power BI's table query
engine (`SUMMARIZECOLUMNS`) can collapse a same-table `CALCULATE` filter
that matches zero rows into `BLANK()` rather than a literal `0`, even
though `DIVIDE`'s own documented behavior only substitutes blank when the
*denominator* is zero. Fix: append `+ 0` to the end of the measure, which
coerces any blank result back to a real zero (`BLANK() + 0 = 0` in DAX) —
a small, well-known workaround for this exact class of bug. Caught the
same way as the `PeopleCaughtParsed` and `AvyYear` bugs before it: by
checking that a number which should exist (0%, not "no data") actually
rendered instead of assuming a clean-looking chart was correct. See
`fact_table_data_dictionary.md` for the full writeup.

**Caveats to carry onto the page:** none beyond what's already built in —
this page's entire content *is* caveats. Worth remembering, though: the
page documents known limitations, but it can't catch limitations nobody's
found yet. Treat it as the floor of what's uncertain about this dataset,
not the ceiling.
