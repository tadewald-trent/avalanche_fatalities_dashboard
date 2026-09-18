# DimActivityCategory Data Dictionary

**File:** `data/processed/dim_activity_category.csv`
**Built by:** `data/processed/build_activity_category.py`
**Source:** `PrimaryActivity` column of `avalanche_fatalities_clean.csv` (24 distinct values, 1,016 rows, all mapped)

A lookup/dimension table, not a column baked onto the fact table — same
pattern as `DimSeason`. Join `PrimaryActivity` to
`avalanche_fatalities_clean[PrimaryActivity]` in Power BI to bring
`ActivityCategory` onto any Q2 (human-factors) visual.

## Why this exists

CAIC's raw data has 24 distinct `PrimaryActivity` values, from
Backcountry Tourer (287 rows) down to single-row categories like Ranger and
Human-Powered Guide. That's too granular to chart directly and too sparse in
the tail to be statistically meaningful on its own — this table collapses it
to 6 categories built around one framing question: **how did this person end
up in avalanche terrain, and by what kind of choice?**

That framing follows directly from Tremper's "it's not the avalanche, it's
the decision" argument (see `research_questions.md`, Q2) — the human-factors
story is fundamentally about voluntary exposure, so grouping by *what kind of
terrain someone chose to be in* tells a more useful story than grouping by
literal job title/activity alone.

**Revision, same day:** the first pass grouped by *access mode* — Sidecountry
Rider was lumped with Inbounds Rider into a "Lift/Resort-Accessed Riding"
bucket, since both start from a lift. Trent caught that this was the wrong
axis: the variable that actually matters for avalanche risk is whether the
terrain is **avalanche-controlled**, not how you reached it. Inbounds terrain
has patrol actively doing mitigation work on it; sidecountry, by definition,
doesn't — once you duck the rope you're in the same uncontrolled snowpack as
any backcountry tourer, you just got there differently. Sidecountry Rider
moved into the backcountry/uncontrolled-terrain category as a result. This is
a better distinction than the original one, not just a different one — worth
noting here as an example of the categorization being genuinely revisable,
not locked in after the first pass.

**Important: unlike the `SettingLabel` decode (`BC`/`SA`/`TN`/etc.), CAIC
never published an official grouping for `PrimaryActivity`.** There is no
primary source to verify this categorization against — it's an analytical
judgment call, reasoned through and confirmed with Trent on 2026-09-15 before
building, not a fact pulled from CAIC. Treat it as a modeling choice that
could reasonably be made differently, not as ground truth.

## Columns

| Column | Meaning |
|---|---|
| `PrimaryActivity` | The raw CAIC value, unchanged — the join key back to the fact table. |
| `ActivityCategory` | One of the 6 categories below. |
| `ActivityCategorySortOrder` | 1–6, for chart axis ordering (biggest/most-central story first; the catch-all bucket last regardless of its row count, since it isn't a coherent category to lead with). |

## The 6 categories

| Category | Raw values folded in | Rows |
|---|---|---|
| **Backcountry Recreation** — any accident on terrain with no avalanche mitigation being done, regardless of how it was reached | Backcountry Tourer, Hiker, Hybrid Tourer, Sidecountry Rider | 443 |
| **Motorized Backcountry Recreation** — same uncontrolled terrain as category 1, kept separate for the motorized/human-powered distinction | Snowmobiler, Snowbiker, Hybrid Rider | 278 |
| **Inbounds (Avalanche-Controlled Terrain)** — kept standalone despite its small size; "how dangerous is controlled terrain" is a distinct, commonly-asked question | Inbounds Rider | 43 |
| **Climbing/Mountaineering** | Climber | 120 |
| **Guides & Guided Clients** — professional guiding context, any travel mode | Mechanized Guided Client, Mechanized Guide, Human-Powered Guide, Human-Powered Guided Client | 19 |
| **Occupational, Passive & Other** — deliberately heterogeneous, see caveat below | Ski Patroller, Highway Personnel, Others at Work, Resident, Motorist, Miner, Hunter, Snowplayer, Misc Recreation, Rescuer, Ranger | 113 |

Total: 1,016 — every fact-table row lands in exactly one category (validated
by the build script; it raises an error if the raw data ever adds a
25th `PrimaryActivity` value this mapping doesn't know about).

## Two judgment calls, made deliberately, not defaulted to

**1. Motorized Backcountry Recreation is kept separate from Backcountry
Recreation**, even though both happen on the same uncontrolled terrain.
Motorized vs. human-powered access is one of the most-discussed
human-factors distinctions in avalanche literature — different group
dynamics, different terrain choices, "highmarking" as its own
well-documented hazard pattern. Collapsing the two into one bucket would
erase a genuinely interesting split, and the raw counts (443 vs. 278) show
they're both large enough to stand alone anyway. (Originally named
"Snowmobiling," briefly "Backcountry Recreation (Uncontrolled Terrain)" for
category 1 — both renamed same day: "Motorized Backcountry Recreation" to
make the uncontrolled-terrain/motorized-access framing explicit, then the
"(Uncontrolled Terrain)" qualifier dropped from category 1's label per
Trent's preference for the shorter "Backcountry Recreation" — the
uncontrolled-terrain framing still lives in this dictionary's prose and the
category description above, just not in the label itself.)

**2. Ski Patroller sits in "Occupational, Passive & Other," not "Inbounds
(Avalanche-Controlled Terrain),"** even though the physical terrain is
identical to Inbounds Rider. The reasoning: a patroller doing avalanche-
control work is making a professional decision to be in that terrain, not a
recreational one — the framing question is about *why* someone was there,
not just *where*.

## Caveat: "Occupational, Passive & Other" is a deliberate grab-bag

This bucket does **not** mean one clean thing, and should be labeled as
heterogeneous wherever it appears on a chart or in a write-up — never
presented as if it were a coherent activity type the way the other five are.
It mixes three genuinely different situations:

- **True occupational exposure** — Highway Personnel, Others at Work, Miner,
  Ranger, Rescuer, Ski Patroller: people doing their job in avalanche
  terrain.
- **Passive/incidental exposure** — Resident, Motorist: the avalanche came to
  them (their house, their car on a road); this is close to the opposite of
  a voluntary backcountry-terrain decision.
- **Small leftover recreational categories** — Hunter, Snowplayer, Misc
  Recreation: real recreational activity, but each too small (3–12 rows) to
  support its own category without fragmenting the chart further.

It was kept merged into one bucket — rather than split into, say, an
"Occupational" and a separate "Passive/Other" category — specifically to
keep the total at ~6 categories as planned in `research_questions.md`. That's
a compromise for chart legibility, not a claim that a highway worker, a
sleeping resident, and a hunter share a common story. If a future finding on
the Q2 page turns out to hinge on this bucket specifically, that's a signal
to split it rather than force a conclusion out of it as-is.

**Decision, 2026-09-15: the Q2 bar chart uses Power BI's default value-sort
(largest `Total Fatalities` first), not the `ActivityCategorySortOrder`
column this table provides.** `ActivityCategorySortOrder` was built
specifically so "Occupational, Passive & Other" could sit last on purpose,
regardless of its row count — with value-sort, it instead lands wherever its
raw size happens to rank it (currently 4th of 6, ahead of Inbounds and
Guides). That's not wrong, but it means the bar's position no longer signals
anything about the bucket being a catch-all — that signal has to come from
elsewhere on the page now (e.g., a caveat annotation), not from where the bar
sits. Kept as a deliberate choice, made with the tradeoff understood, not an
oversight. `ActivityCategorySortOrder` is still in the table if this
decision ever gets revisited.

## Rebuilding this table

If the raw accident data ever adds a new `PrimaryActivity` value (a future
CAIC export, a new season), `build_activity_category.py` will fail loudly
with the exact unmapped value rather than silently dropping rows — add it to
the `ACTIVITY_CATEGORY` dict, decide which of the 6 categories it belongs in
(or whether a 7th is warranted), and re-run.
