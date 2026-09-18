# CAIC Correspondence: `Setting` Column Codes

**Contact:** Spencer Logan, Colorado Avalanche Information Center
**Date:** 2026
**Resolved:** The meaning of the `Setting` column's short codes, which are not
defined anywhere in the source workbook (including its built-in summary tabs).

## Why this needed asking

The accident database's `Setting` column uses short codes (`BC`, `SA`, `TN`,
`RD`, `RS`, `MN`, and one row marked `SA-closed terrain`) with no legend in
the file. Cross-referencing against `PrimaryActivity` made most of them
guessable (`BC` = Backcountry, `SA` = Ski Area, `MN` = Mine), but two
(`TN`, `RS`) weren't guessable with any confidence, so rather than encode a
guess into the dataset, the question went directly to CAIC.

## The email

> Hi Spencer,
>
> My name is Trent Tadewald, I live in Breckenridge and I'm an avid
> backcountry snowboarder. I'm building a data analyst portfolio project
> using CAIC's public accident database (the file linked from the
> Statistics and Reporting page), analyzing long-term fatality trends
> alongside CAIC's own engagement metrics from your annual reports. I'm
> citing CAIC per the file's request, and I'm happy to share the finished
> project once it's done in case it's useful to have another example of
> how the data gets used.
>
> One quick question: the `Setting` column uses codes (`BC`, `SA`, `TN`,
> `RD`, `RS`, `MN`, and one row marked `SA-closed terrain`) that I can't
> find defined anywhere in the workbook, including the built-in summary
> tabs. I've made an educated guess based on cross-referencing against the
> `PrimaryActivity` column (e.g. `BC` = Backcountry, `SA` = Ski Area,
> `MN` = Mine), but I'd rather use the real definitions than a guess,
> especially for `TN` and `RS`, which I can't seem to figure out.
>
> Would you be able to confirm what each code stands for? No rush at all,
> happy to work around it in the meantime and update the project once I
> hear back.
>
> Thanks for maintaining this dataset, it's great to work with data that
> relates to something I'm passionate about!
>
> Best,
> Trent Tadewald

## The reply

> Trent,
>
> I look forward to your finished project. I always enjoy seeing how folks
> use and combine our data. One thing to note with `Setting` and all other
> categorical variables is that they are the best guess of the investigator.
> Each report may have been compiled and investigated by someone different,
> and everything outside of Colorado was not done by CAIC staff. That's
> something to keep in mind with long-term trends and the database.
>
> Spencer

Spencer's reply confirmed the code definitions inline (sent as a follow-up
list) and, unprompted, raised a caveat about the whole categorical-field
approach that turned out to matter well beyond just `Setting` (see below).

## Confirmed code definitions

| Code | Meaning |
|---|---|
| `BC` | Backcountry |
| `SA` | Ski area |
| `SA-closed terrain` | Ski area, closed terrain (rolled into `SA` for analysis; not treated as a distinct category) |
| `TN` | Town/urban |
| `RD` | Road |
| `RS` | Railroad |
| `MN` | Mine |

## The bigger takeaway

Spencer's caveat, that `Setting` and every other categorical field is "the
best guess of the investigator," not a standardized taxonomy, and that
incidents outside Colorado weren't investigated by CAIC staff at all, is the
direct source of the "investigator judgment, not a standardized taxonomy"
caveat that appears throughout this project (see the Data Quality appendix
in [`research_questions.md`](research_questions.md) and
[`fact_table_data_dictionary.md`](fact_table_data_dictionary.md)). It's also
why Colorado-specific comparisons (like Q3) are treated as more reliable
than nationwide ones: Colorado's rows are the ones CAIC staff investigated
directly.
