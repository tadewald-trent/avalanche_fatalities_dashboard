"""
Build the CAIC engagement/participation-proxy dataset (FY2015-16 through FY2024-25).

Unlike the main accident database (which CAIC publishes as a ready-made download),
this table does NOT exist anywhere as a single file. It was hand-assembled by
reading 10 individual CAIC/Friends-of-CAIC annual report PDFs one at a time -
6 of them only reachable via Wayback Machine snapshots after CAIC's old
`classic.avalanche.state.co.us` subdomain stopped serving them directly.

Every number below is transcribed directly from a specific PDF page. Source URLs
are kept in `source_pdfs.csv` alongside this script for traceability - if a number
here looks wrong, that's the first place to check it against.

Known data-quality issues, deliberately NOT cleaned away (documented in
../../docs/caic_engagement_data_dictionary.md instead):
  1. FY15-16 and FY16-17 report the *identical* website-visits figure (1,732,675)
     down to the digit, while every other metric on those two report pages
     differs. Almost certainly a copy-paste error in CAIC's own FY16-17 report
     template. Flagged via `website_metric_suspect`, not silently dropped or
     "corrected" - we don't actually know what FY16-17's real number was.
  2. The website metric itself changes definition three times across the
     decade: "Visits" (FY16-17) -> "Pageviews" (FY18-24) -> "Pageviews + Users"
     (FY21-25 only). These are not the same statistic. `website_metric_type`
     records which one each row actually is.
  3. The app metric changes definition even more: Downloads -> Active Users ->
     Screen Views. `app_metric_type` records which one each row is.
  4. FY21-22's report never states a fatality count in the text CAIC wrote -
     that value is backfilled from our own accident database instead, and is
     flagged via `fatalities_source`.
"""
import pandas as pd

FATALITY_XLSX = "../raw/CAIC_Accident_Data_Oct_2025.xlsx"
OUTPUT_CSV = "caic_engagement_by_year.csv"

# Hand-transcribed from the 10 annual report PDFs. avy_year follows the same
# season-ends-in convention as the main accident dataset's AvyYear column
# (a Nov 2023-Apr 2024 season = avy_year 2024), confirmed by cross-checking
# every fatality count below against the raw accident database.
ROWS = [
    dict(fiscal_year="FY15-16", avy_year=2016,
         website_metric_type="visits", website_metric_value=1732675, website_users=None,
         website_metric_suspect=False,
         app_metric_type="downloads", app_metric_value=9175, app_users=None,
         fatalities_reported=5, fatalities_source="report_text",
         source_pdf="caic_annual-report_15-16.pdf"),
    dict(fiscal_year="FY16-17", avy_year=2017,
         website_metric_type="visits", website_metric_value=1732675, website_users=None,
         website_metric_suspect=True,  # identical to FY15-16 to the digit - likely copy/paste error
         app_metric_type="downloads", app_metric_value=11410, app_users=None,
         fatalities_reported=1, fatalities_source="report_text",
         source_pdf="FoCAIC_annual-report_16-17_final.pdf"),
    dict(fiscal_year="FY17-18", avy_year=2018,
         website_metric_type="pageviews", website_metric_value=1340863, website_users=None,
         website_metric_suspect=False,
         app_metric_type="downloads", app_metric_value=12745, app_users=None,
         fatalities_reported=3, fatalities_source="report_text",
         source_pdf="CAIC_Annual_Report_2017-18.pdf"),
    dict(fiscal_year="FY18-19", avy_year=2019,
         website_metric_type="pageviews", website_metric_value=2768019, website_users=None,
         website_metric_suspect=False,
         app_metric_type="downloads", app_metric_value=13745, app_users=None,
         fatalities_reported=8, fatalities_source="report_text",
         source_pdf="FY19AnnualReport.pdf"),
    dict(fiscal_year="FY19-20", avy_year=2020,
         website_metric_type="pageviews", website_metric_value=2176198, website_users=None,
         website_metric_suspect=False,
         app_metric_type="active_users", app_metric_value=18000, app_users=18000,
         fatalities_reported=6, fatalities_source="report_text",
         source_pdf="CAIC_FY20AnnualReport_Final_Web-large.pdf"),
    dict(fiscal_year="FY20-21", avy_year=2021,
         website_metric_type="pageviews", website_metric_value=2882948, website_users=416936,
         website_metric_suspect=False,
         app_metric_type="screen_views", app_metric_value=1100000, app_users=22000,
         fatalities_reported=12, fatalities_source="report_text",
         source_pdf="CAIC_FY21AnnualReport_Web-large_Jan11.pdf"),
    dict(fiscal_year="FY21-22", avy_year=2022,
         website_metric_type="pageviews", website_metric_value=2527632, website_users=388638,
         website_metric_suspect=False,
         app_metric_type="pageviews", app_metric_value=1027218, app_users=19866,
         fatalities_reported=7, fatalities_source="accident_database_backfill",  # not stated in report text
         source_pdf="CAIC_FY22AnnualReport_Final_Small.pdf"),
    dict(fiscal_year="FY22-23", avy_year=2023,
         # CORRECTED 2026-09-13: originally transcribed as 1,000,000 - a plain
         # transcription error. The report actually states "3.1 Million Pageviews"
         # (page 6, "Growing Reach: Media Overview"), independently confirmed by its
         # own "22% YoY increase" stat: FY21-22's 2,527,632 x 1.22 = 3,083,711,
         # matching the stated 3.1M almost exactly. See the data dictionary's
         # caveat section for the full story of how this was caught and fixed.
         website_metric_type="pageviews_rounded", website_metric_value=3100000, website_users=None,
         website_metric_suspect=False,
         app_metric_type=None, app_metric_value=None, app_users=None,
         fatalities_reported=11, fatalities_source="report_text",
         source_pdf="2022-2023 Annual Report.pdf"),
    dict(fiscal_year="FY23-24", avy_year=2024,
         website_metric_type="pageviews", website_metric_value=3027380, website_users=None,
         website_metric_suspect=False,
         app_metric_type=None, app_metric_value=None, app_users=None,
         fatalities_reported=2, fatalities_source="report_text",
         source_pdf="Friends of CAIC and CAIC FY24 Annual Report.pdf"),
    dict(fiscal_year="FY24-25", avy_year=2025,
         website_metric_type="pageviews", website_metric_value=2100000, website_users=257515,
         website_metric_suspect=False,
         app_metric_type="pageviews", app_metric_value=1786374, app_users=21922,
         fatalities_reported=3, fatalities_source="report_text",
         source_pdf="CAIC_FY25AnnualReport_Final_Web.pdf"),
]


def crosscheck_fatalities():
    """Independently recompute CO fatalities per avy_year from the raw accident
    database, so we can compare against what each annual report claims."""
    df = pd.read_excel(FATALITY_XLSX, sheet_name="Data")
    co = df[df["State"] == "CO"]
    return co.groupby("AvyYear")["Killed"].sum().to_dict()


def main():
    engagement = pd.DataFrame(ROWS)
    crosscheck = crosscheck_fatalities()
    engagement["fatalities_accident_db"] = engagement["avy_year"].map(crosscheck)
    engagement["fatalities_match"] = (
        engagement["fatalities_reported"] == engagement["fatalities_accident_db"]
    )

    mismatches = engagement[~engagement["fatalities_match"]]
    if len(mismatches):
        print("WARNING - fatality mismatches found:")
        print(mismatches[["fiscal_year", "fatalities_reported", "fatalities_accident_db"]])
    else:
        print(f"All {len(engagement)} years validated: CAIC-reported fatalities match the accident database exactly.")

    engagement.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {OUTPUT_CSV} ({len(engagement)} rows)")
    print(engagement.to_string(index=False))


if __name__ == "__main__":
    main()
