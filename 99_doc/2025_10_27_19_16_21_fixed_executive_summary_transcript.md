# Fixed Executive Summary

**Processing Date:** 2025-10-27 19:16:21
**Source File:** fixed_executive_summary.txt
**Total Chunks:** 1

---

let
    OvertimeData = Excel.CurrentWorkbook(){[Name="OVERTIME_MASTER"]}[Content],
    TimeOffData = Excel.CurrentWorkbook(){[Name="TIME_OFF_MASTER"]}[Content],
    CurrentYear = 2025,  // Hard-coded to ensure it works
    
    // Filter current year data
    CurrentYearOT = Table.SelectRows(OvertimeData, each [Year] = CurrentYear),
    CurrentYearTO = Table.SelectRows(TimeOffData, each [Year] = CurrentYear),
    
    // OVERTIME METRICS - Fixed text matching
    TotalCompTime = List.Sum(Table.SelectRows(CurrentYearOT, each [Pay Type] = "1.0 Comp Time" or [Pay Type] = "1.5 Comp Time")[Hours]),
    TotalCashOT = List.Sum(Table.SelectRows(CurrentYearOT, each [Pay Type] = "1.5 Cash" or [Pay Type] = "2.0 Cash")[Hours]),
    TotalOTCost = List.Sum(Table.AddColumn(CurrentYearOT, "Cost", each [Rate] * [Hours])[Cost]),
    
    // TIME OFF METRICS - Fixed text matching
    TotalInjuredDuty = List.Sum(Table.SelectRows(CurrentYearTO, each [Reason] = "Injured on Duty")[Hours]),
    TotalMilitaryTime = List.Sum(Table.SelectRows(CurrentYearTO, each [Reason] = "Military Leave")[Hours]),
    TotalSLEOSick = List.Sum(Table.SelectRows(CurrentYearTO, each [Reason] = "SLEO III Sick (Hours)")[Hours]),
    TotalPEOSick = List.Sum(Table.SelectRows(CurrentYearTO, each [Reason] = "PEO Sick (Hours)")[Hours]),
    TotalSickDays = Table.RowCount(Table.SelectRows(CurrentYearTO, each [Reason] = "Sick (Days)")),
    
    // OFFICER COUNTS
    ActiveOfficers = Table.RowCount(Table.Distinct(CurrentYearOT, {"Employee"})),
    
    // Create executive summary using #table syntax for better display
    Result = #table(
        {"Metric", "Value"},
        {
            {"Accrued Comp Time (Hours)", TotalCompTime},
            {"Accrued Overtime (Hours)", TotalCashOT},
            {"Total Overtime Cost YTD", TotalOTCost},
            {"Injured on Duty (Hours)", TotalInjuredDuty},
            {"Military Leave (Hours)", TotalMilitaryTime},
            {"SLEO III Sick (Hours)", TotalSLEOSick},
            {"PEO Sick (Hours)", TotalPEOSick},
            {"Sick Days (Count)", TotalSickDays},
            {"Active Officers", ActiveOfficers},
            {"Avg Comp Time Per Officer", if ActiveOfficers > 0 then TotalCompTime / ActiveOfficers else 0},
            {"Avg Cash OT Per Officer", if ActiveOfficers > 0 then TotalCashOT / ActiveOfficers else 0}
        }
    )
in
    Result

