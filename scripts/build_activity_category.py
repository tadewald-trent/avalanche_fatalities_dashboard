"""
Build DimActivityCategory - a lookup table collapsing the 24 raw
PrimaryActivity values (avalanche_fatalities_clean.csv) into 6 broader
categories for the Q2 (human-factors) report page.

This is a lookup/dimension table, not a column baked onto the fact table -
same pattern as DimSeason. Join it to avalanche_fatalities_clean[PrimaryActivity]
in Power BI to get ActivityCategory on any Q2 visual.

Unlike the Setting-code decode (data/processed/build_clean_fact_table.py),
CAIC never defined an official grouping for PrimaryActivity - there's no
primary source to verify this against. The categories below are an analytical
judgment call, reasoned through with the following framing (confirmed with
Trent 2026-09-15 before building, revised same day after Trent caught a flaw
in the first pass - see below): Tremper's "it's not the avalanche, it's the
decision" argument is fundamentally about VOLUNTARY exposure to avalanche
terrain, so the split should track *what kind of terrain someone chose to be
in*, not just their literal job title/activity.

The first version of this table grouped by ACCESS MODE - Sidecountry Rider
was lumped with Inbounds Rider into "Lift/Resort-Accessed Riding" because
both start from a lift. Trent caught that this is the wrong axis: the
variable that actually matters for avalanche risk is whether the terrain is
AVALANCHE-CONTROLLED, not how you got to it. Inbounds terrain has patrol
actively doing mitigation work on it; sidecountry, by definition, doesn't -
once you duck the rope you're in the same uncontrolled snowpack as any
backcountry tourer, you just got there differently. Sidecountry Rider moved
into the backcountry/uncontrolled-terrain category as a result.

Six categories:
  1. Backcountry Recreation - human-powered touring,
     hiking, AND lift/resort-accessed sidecountry riding - anyone whose
     accident happened in terrain with no avalanche mitigation being done on
     it, regardless of how they reached it.
  2. Motorized Backcountry Recreation - snowmobiles and snowmobile-adjacent
     riding, on the same uncontrolled terrain as category 1, kept separate
     because motorized vs. human-powered access is its own well-documented
     human-factors distinction (see judgment call 1 in the data dictionary)
  3. Inbounds (Avalanche-Controlled Terrain) - Inbounds Rider only. Kept as
     its own category despite being small (43 rows) because "how dangerous is
     controlled terrain" is a genuinely distinct and commonly-asked question,
     not because of its size.
  4. Climbing/Mountaineering
  5. Guides & Guided Clients - professional guiding context, any travel mode
  6. Occupational, Passive & Other - a deliberate grab-bag: true occupational
     exposure (highway crews, miners, ski patrol doing avalanche-control work),
     passive/incidental exposure (residents, motorists - the avalanche came to
     them, not the other way around), and small leftover recreational
     categories that don't clear double digits individually (hunters,
     snowplayers, misc recreation). This bucket does NOT mean one clean thing
     - see the data dictionary caveat. Keep it labeled as heterogeneous on any
     chart rather than implying it's a single coherent activity type.

Two judgment calls worth flagging explicitly (both confirmed with Trent before
building, not just defaulted to silently):
  - Ski Patroller goes in bucket 6 (Occupational), not bucket 3 (Inbounds
    terrain), because they're doing avalanche-mitigation work, not recreating
    - even though the physical terrain is the same as Inbounds Rider.
  - Bucket 6 stays merged (Occupational + Passive + Other) rather than split
    further, to keep the total at ~6 categories as planned in
    research_questions.md - at the cost of that bucket being a mix of quite
    different situations. This is a compromise, not a claim that these are
    all the same thing.
"""
import pandas as pd

FACT_CSV = "avalanche_fatalities_clean.csv"
OUTPUT_CSV = "dim_activity_category.csv"

# Every PrimaryActivity value that exists in the fact table (24, confirmed by
# reading avalanche_fatalities_clean.csv directly - see the validation step
# below, which fails loudly if the source data ever adds a 25th value this
# mapping doesn't know about).
ACTIVITY_CATEGORY = {
    # 1. Backcountry Recreation
    "Backcountry Tourer": "Backcountry Recreation",
    "Hiker": "Backcountry Recreation",
    "Hybrid Tourer": "Backcountry Recreation",
    "Sidecountry Rider": "Backcountry Recreation",
    # 2. Motorized Backcountry Recreation
    "Snowmobiler": "Motorized Backcountry Recreation",
    "Snowbiker": "Motorized Backcountry Recreation",
    "Hybrid Rider": "Motorized Backcountry Recreation",
    # 3. Inbounds (Avalanche-Controlled Terrain)
    "Inbounds Rider": "Inbounds (Avalanche-Controlled Terrain)",
    # 4. Climbing/Mountaineering
    "Climber": "Climbing/Mountaineering",
    # 5. Guides & Guided Clients
    "Mechanized Guided Client": "Guides & Guided Clients",
    "Mechanized Guide": "Guides & Guided Clients",
    "Human-Powered Guide": "Guides & Guided Clients",
    "Human-Powered Guided Client": "Guides & Guided Clients",
    # 6. Occupational, Passive & Other (deliberately heterogeneous - see docstring)
    "Ski Patroller": "Occupational, Passive & Other",
    "Highway Personnel": "Occupational, Passive & Other",
    "Others at Work": "Occupational, Passive & Other",
    "Resident": "Occupational, Passive & Other",
    "Motorist": "Occupational, Passive & Other",
    "Miner": "Occupational, Passive & Other",
    "Hunter": "Occupational, Passive & Other",
    "Snowplayer": "Occupational, Passive & Other",
    "Misc Recreation": "Occupational, Passive & Other",
    "Rescuer": "Occupational, Passive & Other",
    "Ranger": "Occupational, Passive & Other",
}

# Sort order for charts - roughly biggest/most-central story first, catch-all
# bucket last regardless of its row count, since it's not a coherent category
# to lead with.
CATEGORY_SORT_ORDER = {
    "Backcountry Recreation": 1,
    "Motorized Backcountry Recreation": 2,
    "Inbounds (Avalanche-Controlled Terrain)": 3,
    "Climbing/Mountaineering": 4,
    "Guides & Guided Clients": 5,
    "Occupational, Passive & Other": 6,
}


def main():
    fact = pd.read_csv(FACT_CSV)
    raw_values = set(fact["PrimaryActivity"].dropna().unique())
    mapped_values = set(ACTIVITY_CATEGORY.keys())

    unmapped = raw_values - mapped_values
    stale = mapped_values - raw_values
    if unmapped:
        raise ValueError(
            f"PrimaryActivity value(s) in the fact table with no category mapping: "
            f"{sorted(unmapped)} - add them to ACTIVITY_CATEGORY before building."
        )
    if stale:
        print(
            f"NOTE: mapping has {sorted(stale)} which no longer appear in the fact "
            f"table - harmless, but worth pruning next time this script is touched."
        )

    dim = pd.DataFrame(
        [{"PrimaryActivity": k, "ActivityCategory": v} for k, v in ACTIVITY_CATEGORY.items()]
    )
    dim["ActivityCategorySortOrder"] = dim["ActivityCategory"].map(CATEGORY_SORT_ORDER)
    dim = dim.sort_values(["ActivityCategorySortOrder", "PrimaryActivity"]).reset_index(drop=True)

    # Validation: row counts per category, cross-checked against the fact table,
    # confirming every one of the 1,016 rows lands in exactly one category.
    counts = fact["PrimaryActivity"].value_counts()
    dim["RowCount"] = dim["PrimaryActivity"].map(counts).fillna(0).astype(int)
    category_totals = dim.groupby("ActivityCategory", sort=False)["RowCount"].sum()
    category_totals = category_totals.reindex(
        sorted(CATEGORY_SORT_ORDER, key=CATEGORY_SORT_ORDER.get)
    )

    print("ActivityCategory totals:")
    print(category_totals.to_string())
    print(f"\nSum of category totals: {category_totals.sum()}")
    print(f"Fact table rows with a non-null PrimaryActivity: {fact['PrimaryActivity'].notna().sum()}")
    assert category_totals.sum() == fact["PrimaryActivity"].notna().sum(), (
        "Category totals don't add up to the fact table's PrimaryActivity row count - "
        "something is double-mapped or dropped."
    )
    print("Validation passed: every PrimaryActivity row is accounted for in exactly one category.\n")

    # RowCount was only for validation printing above - drop it from the
    # lookup table itself, since a lookup table shouldn't carry a count that
    # changes as soon as the fact table is refreshed.
    dim = dim.drop(columns=["RowCount"])
    dim.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {OUTPUT_CSV} ({len(dim)} rows)")
    print(dim.to_string(index=False))


if __name__ == "__main__":
    main()
