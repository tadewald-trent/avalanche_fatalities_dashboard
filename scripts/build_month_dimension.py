"""
Build DimMonth - a small lookup table giving each calendar month (1-12, the
raw `MM` column in avalanche_fatalities_clean.csv) a name and a SEASON-order
position, for the Q3 (seasonality) timing chart.

Why this exists: MM is a plain calendar month (1=January ... 12=December),
but an avalanche season runs November -> the following October, not
January -> December. Charting Total Fatalities by MM with the default
sort (1, 2, 3, ...) would split the winter season across both ends of the
axis - November and December would land at the far right, after April and
May, even though they're the START of the season a viewer actually cares
about. Same category of bug as the SeasonLabel and Decade sort issues hit
earlier in this project - a "Sort by column" problem, just for months
instead of seasons/decades.

This is a mechanical, non-judgment-call lookup (unlike SettingLabel or
DimActivityCategory) - there's no ambiguity in "what season-order position
does March occupy" - so it's a simple, fully deterministic table.
"""
import pandas as pd

FACT_CSV = "avalanche_fatalities_clean.csv"
OUTPUT_CSV = "dim_month.csv"

# Season runs Nov (order 1) through the following Oct (order 12).
MONTH_INFO = {
    11: ("November", 1),
    12: ("December", 2),
    1:  ("January", 3),
    2:  ("February", 4),
    3:  ("March", 5),
    4:  ("April", 6),
    5:  ("May", 7),
    6:  ("June", 8),
    7:  ("July", 9),
    8:  ("August", 10),
    9:  ("September", 11),
    10: ("October", 12),
}


def main():
    fact = pd.read_csv(FACT_CSV)
    raw_months = set(fact["MM"].dropna().unique().tolist())
    mapped_months = set(MONTH_INFO.keys())

    unmapped = raw_months - mapped_months
    if unmapped:
        raise ValueError(f"MM value(s) in the fact table with no month mapping: {sorted(unmapped)}")

    dim = pd.DataFrame(
        [{"MM": mm, "MonthName": name, "SeasonMonthOrder": order} for mm, (name, order) in MONTH_INFO.items()]
    )
    dim = dim.sort_values("SeasonMonthOrder").reset_index(drop=True)

    # Validation: row counts per month, cross-checked against the fact table.
    counts = fact["MM"].value_counts()
    dim["RowCount"] = dim["MM"].map(counts).fillna(0).astype(int)
    print("Rows by month (season order, Nov -> Oct):")
    print(dim.to_string(index=False))
    print(f"\nSum of RowCount: {dim['RowCount'].sum()}, fact table rows: {len(fact)}")
    assert dim["RowCount"].sum() == len(fact), "Month counts don't add up to the fact table's row count."
    print("Validation passed: every fact-table row's MM maps to exactly one month.\n")

    dim = dim.drop(columns=["RowCount"])
    dim.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {OUTPUT_CSV} ({len(dim)} rows)")


if __name__ == "__main__":
    main()
