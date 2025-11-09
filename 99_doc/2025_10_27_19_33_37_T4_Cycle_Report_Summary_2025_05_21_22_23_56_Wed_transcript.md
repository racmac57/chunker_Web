# T4 Cycle Report Summary 2025 05 21 22 23 56 Wed

**Processing Date:** 2025-10-27 19:33:37
**Source File:** T4_Cycle_Report_Summary_2025_05_21_22_23_56_Wed.md
**Total Chunks:** 1

---

# 🚓 T4 CAD + RMS Report Cycle Project Summary

**Date:** 2025-05-22  
**Analyst:** Code Copilot

---

## ✅ Project Purpose

Merge CAD and RMS data into a unified reporting model for weekly report generation with automated 7-Day, 28-Day, and YTD cycle classification. ---

## 🧱 Queries Created

### 1. `Joined_CAD_RMS`
Merges and normalizes CAD/RMS data:
- Adds MatchKey: `CAD_ReportNumberNew` = `Text.Start(RMS_Case Number, 8)`
- Merges RMS fields: `RMS_IncidentDate`, `RMS_Block`, `RMS_TimeOfDay`, `RMS_IncidentTypes`
- Adds:
  - `Block_Final`: coalesced from CAD then RMS
  - `Has_RMS_Record`: true if RMS_IncidentDate exists
  - `WeekNumber`, `CycleNumber`
  - `CurrentCycle`: "7-Day", "28-Day", or "YTD"
  - `ReportName`: e.g. T4_C01W03

### 2. `Cycle Summary`
Groups `Joined_CAD_RMS` data by:
- `CycleNumber`, `WeekNumber`, `CurrentCycle`, `ReportName`
- Measures:
  - `Total Incidents`
  - `Incident Type Breakdown` (from `RMS_IncidentTypes`)

---

## 🛠 Issues & Fixes

| Issue | Fix |
|------|-----|
| Date vs. DateTime | Used `Date.From(...)` for safe comparison |
| Cyclic reference | Ensured `Cycle Summary` references only `Joined_CAD_RMS` |
| Invalid list transform | Switched from `List.Transform(_, ...)` to `Table.Column(_, ...)` |
| Null group key values | Filtered with `Table.SelectRows` before grouping |
| Fallback column logic | Used `try` + `otherwise null` where needed |

---

## 📎 Current M Code for `Cycle Summary`

```powerquery
let
    Source = #"Joined_CAD_RMS",

    Valid = Table.SelectRows(Source, each 
        try (
            ([RMS_IncidentDate] <> null or [#"CAD_Time of Call"] <> null) and
            [CycleNumber] <> null and
            [WeekNumber] <> null and
            [CurrentCycle] <> null and
            [ReportName] <> null
        ) otherwise false),

    Grouped = Table.Group(Valid, {"CycleNumber", "WeekNumber", "CurrentCycle", "ReportName"}, {
        {"Total Incidents", each Table.RowCount(_), Int64.Type},
        {"Incident Type Breakdown", each 
            let typeList = List.RemoveNulls(List.Distinct(Table.Column(_, "RMS_IncidentTypes")))
            in Text.Combine(typeList, ", "), type text}
    })

in
    Grouped
```

---

## 🔐 Next Steps

- Add `StartOfWeek`, `EndOfWeek` columns for calendar visualization
- Add TimeOfDay breakdown, export automation
- Optional: Turn `ReportDate` into a Parameter


# Append more detailed descriptions to the markdown summary
enhanced_summary = summary_text + """

---

## 🧾 Query Details & Column Purpose

### 🔍 `Joined_CAD_RMS` – Description of Columns

| Column              | Purpose |
|---------------------|---------|
| `MatchKey`          | Joins CAD and RMS records based on normalized Report/Case Number |
| `Block_Final`       | Uses `CAD_Block` when present; otherwise `RMS_Block` |
| `Has_RMS_Record`    | Boolean flag (`true`/`false`) indicating whether an RMS record matched |
| `WeekNumber`        | Computed from fixed `ReportDate`, used for week grouping |
| `CycleNumber`       | Rolling 4-week group ID derived from `WeekNumber` |
| `CurrentCycle`      | Classifies incidents into “7-Day”, “28-Day”, or “YTD” windows |
| `ReportName`        | Naming convention for report grouping: `T4_CxxWxx` (cycle/week) |

---

### 📊 `Cycle Summary` – Purpose

The `Cycle Summary` aggregates incident-level data into a weekly report view. It groups records by cycle and week, then calculates:

- Total incident count (`Total Incidents`)
- Breakdown of distinct `RMS_IncidentTypes` in each week/cycle group

This allows reporting by:
- Weekly trends (WeekNumber)
- High-level time windows (CurrentCycle)
- Report grouping (ReportName)

Ideal for dashboard KPIs, summaries, and PDF exports.

""" # Overwrite the file with the enhanced content
file_path.write_text(enhanced_summary)
file_path.name

