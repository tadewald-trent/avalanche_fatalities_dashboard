"""
Build the cleaned FactAvalancheEvents table for Power BI from the raw CAIC
accident workbook.

This is where the *judgment-heavy* cleaning happens (see docs/ for the full
Python-vs-Power-Query rationale) - flags and extractions that deserve to be
reasoned through once, tested, and locked down, rather than redone casually
inside Power Query on every refresh. Mechanical text cleanup (trimming,
case-fixing "Ski"/"SKi", splitting Setting into columns) still happens in
Power Query itself, where it's visible as Applied Steps in the .pbix.

Three enrichments happen here:

1. HasLocation / HasDescription flags - lat/lon of (0,0) is a placeholder,
   not a true zero, for records before real geocoding existed (confirmed:
   100% of pre-2010 rows, 0% of 2020s rows). Description is genuinely absent
   pre-2010, not lost.

2. Setting label decode - BC/SA/TN/RD/RS/MN are never defined anywhere in the
   source workbook (checked every sheet, including the pivot tables - none
   spell them out). CONFIRMED directly by Spencer Logan (CAIC) via email,
   2026-08-25: BC=Backcountry, SA=Ski area (SA-closed terrain folds into SA,
   distinguished instead by the IsClosedTerrain flag - matches how this
   script already split it), TN=Town/urban, RD=Road, RS=Railroad, MN=Mine.
   Two of our original guesses were wrong (TN was guessed as "Transportation
   Corridor", RS as "Residence") - a reminder that UNCONFIRMED labels earn
   that tag for a reason and shouldn't be presented as fact until verified.

   Spencer also flagged an important caveat, carried into the data
   dictionary: Setting and other categorical fields reflect each individual
   investigator's best judgment at the time, not a standardized taxonomy.
   Reports are compiled by different people over the decades, and anything
   outside Colorado was not investigated by CAIC staff at all. Treat
   long-term trends and cross-state comparisons on these fields with that in
   mind - it's a real data-quality caveat, not boilerplate.

3. Description text extraction - the free-text field turns out to be a
   tightly formulaic incident summary, not a narrative (verified by sampling
   all 265 non-null rows before writing any regex). Extracts: whether an
   injury is mentioned, whether a "critical" partial burial is mentioned
   (airway-compromised burial, a real severity tier distinct from a full
   burial), a non-standard cause flag (cornice collapse / serac fall vs.
   ordinary avalanche burial), and a best-effort People Caught count.
   Extraction failures are recorded, not guessed around - see
   `people_caught_parsed`.
"""
import re
import pandas as pd

RAW_XLSX = "../raw/CAIC_Accident_Data_Oct_2025.xlsx"
OUTPUT_CSV = "avalanche_fatalities_clean.csv"

# Confirmed directly by Spencer Logan (CAIC) via email, 2026-08-25. Two of our
# original inferred guesses were wrong (TN, RS) - see the module docstring.
SETTING_LABELS_CONFIRMED = {
    "BC": "Backcountry",
    "SA": "Ski Area",
    "TN": "Town/Urban",
    "RD": "Road",
    "RS": "Railroad",
    "MN": "Mine",
}

WORD_NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def parse_leading_count(text):
    """Best-effort extraction of the leading 'N <activity> caught' count.
    Returns (count_or_None, parsed_ok). 'Multiple' and unparseable leads
    return (None, False) rather than a guessed number."""
    m = re.match(r"^(\d+|one|two|three|four|five|multiple)\b", text.strip(), re.IGNORECASE)
    if not m:
        return None, False
    token = m.group(1).lower()
    if token == "multiple":
        return None, False
    if token.isdigit():
        return int(token), True
    return WORD_NUMBERS[token], True


def parse_injured_count(text):
    """Best-effort extraction of '<N> injured'. Returns None if not present
    or not a parseable number (e.g. bare 'injured' with no count nearby)."""
    m = re.search(r"(\d+|one|two|three|four|five)\s+injured", text, re.IGNORECASE)
    if not m:
        return None
    token = m.group(1).lower()
    return int(token) if token.isdigit() else WORD_NUMBERS[token]


def classify_cause(text):
    t = text.lower()
    if "cornice" in t:
        return "cornice_collapse"
    if "serac" in t:
        return "serac_fall"
    return "standard_burial"


def main():
    df = pd.read_excel(RAW_XLSX, sheet_name="Data")

    # --- Enrichment 1: location / description completeness flags ---
    df["HasLocation"] = ~((df["lat"] == 0) & (df["lon"] == 0))
    df["HasDescription"] = df["Description"].notna()

    # --- Enrichment 2: Setting decode (confirmed by CAIC) ---
    df["SettingCode"] = df["Setting"].str.replace("-closed terrain", "", regex=False)
    df["IsClosedTerrain"] = df["Setting"].str.contains("closed terrain", case=False, na=False)
    df["SettingLabel"] = df["SettingCode"].map(SETTING_LABELS_CONFIRMED)

    # --- Enrichment 3: Description text extraction ---
    has_desc = df["Description"].notna()
    df["MentionsInjured"] = False
    df["MentionsCriticalBurial"] = False
    df["AlternateCause"] = None
    df["PeopleCaught"] = pd.NA
    df["PeopleCaughtParsed"] = False
    df["PeopleInjured"] = pd.NA

    df.loc[has_desc, "MentionsInjured"] = df.loc[has_desc, "Description"].str.contains(
        "injured", case=False, na=False
    )
    df.loc[has_desc, "MentionsCriticalBurial"] = df.loc[has_desc, "Description"].str.contains(
        "critical", case=False, na=False
    )
    df.loc[has_desc, "AlternateCause"] = df.loc[has_desc, "Description"].apply(classify_cause)

    parsed = df.loc[has_desc, "Description"].apply(parse_leading_count)
    df.loc[has_desc, "PeopleCaught"] = [p[0] for p in parsed]
    df.loc[has_desc, "PeopleCaughtParsed"] = [p[1] for p in parsed]
    df.loc[has_desc, "PeopleInjured"] = df.loc[has_desc, "Description"].apply(parse_injured_count)

    # --- Validation / spot checks ---
    n_desc = has_desc.sum()
    n_parsed = df["PeopleCaughtParsed"].sum()
    print(f"Descriptions present: {n_desc}")
    print(f"PeopleCaught successfully parsed: {n_parsed} ({n_parsed/n_desc:.0%})")
    print(f"PeopleCaught NOT parsed (e.g. 'Multiple...'): {n_desc - n_parsed}")
    print(f"Rows mentioning injury: {df['MentionsInjured'].sum()}")
    print(f"Rows mentioning critical burial: {df['MentionsCriticalBurial'].sum()}")
    print(df.loc[has_desc, "AlternateCause"].value_counts().to_string())

    # Sanity check: where PeopleCaught parsed AND Killed is known, caught should
    # never be less than killed (you can't kill more people than were caught).
    # Rows that fail this are a real extraction bug (e.g. "1 skier and 1
    # snowmobiler killed" parses "1" from the leading clause, but the true
    # count is 2) - invalidate rather than ship a wrong number.
    bad_mask = df["PeopleCaughtParsed"] & (df["PeopleCaught"] < df["Killed"])
    n_bad = bad_mask.sum()
    if n_bad:
        print(f"\nSanity check caught {n_bad} bad parse(s) - invalidating rather than shipping wrong values:")
        print(df.loc[bad_mask, ["Location", "Description", "PeopleCaught", "Killed"]].to_string())
        df.loc[bad_mask, "PeopleCaught"] = pd.NA
        df.loc[bad_mask, "PeopleCaughtParsed"] = False
    else:
        print("\nSanity check passed: no row has PeopleCaught < Killed.")

    n_parsed_final = df["PeopleCaughtParsed"].sum()
    print(f"Final PeopleCaught parse rate: {n_parsed_final}/{n_desc} ({n_parsed_final/n_desc:.0%})")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {OUTPUT_CSV} ({len(df)} rows, {len(df.columns)} columns)")


if __name__ == "__main__":
    main()
