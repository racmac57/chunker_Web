# Kpi Query Fixed

**Processing Date:** 2025-10-27 19:19:03
**Source File:** kpi_query_fixed.txt
**Total Chunks:** 1

---

let
    // === EXECUTIVE SUMMARY FOR CHIEF/LEADERSHIP ===
    Source = MVA_MASTER,
    
    // Current month data
    CurrentMonth = Date.Month(DateTime.LocalNow()),
    CurrentYear = Date.Year(DateTime.LocalNow()),
    CurrentMonthData = Table.SelectRows(Source, each 
        [Month] <> null and [Year] <> null and 
        [Month] = CurrentMonth and [Year] = CurrentYear),
    
    // Previous month for comparison
    PrevMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
    PrevYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
    PrevMonthData = Table.SelectRows(Source, each 
        [Month] <> null and [Year] <> null and 
        [Month] = PrevMonth and [Year] = PrevYear),
    
    // === KEY PERFORMANCE INDICATORS ===
    
    // 1. TRAFFIC VOLUME METRICS
    CurrentMVAs = Table.RowCount(CurrentMonthData),
    PrevMVAs = Table.RowCount(PrevMonthData),
    MVAChange = try (CurrentMVAs - PrevMVAs) / PrevMVAs otherwise 0,
    
    // 2. INJURY CRASH METRICS (Fixed with null checks)
    CurrentInjuries = List.Count(List.Select(CurrentMonthData[AllIncidents], each _ <> null and Text.Contains(Text.Lower(_), "injury"))),
    PrevInjuries = List.Count(List.Select(PrevMonthData[AllIncidents], each _ <> null and Text.Contains(Text.Lower(_), "injury"))),
    InjuryChange = try (CurrentInjuries - PrevInjuries) / PrevInjuries otherwise 0,
    
    // 3. HIT-AND-RUN METRICS (Fixed with null checks)
    CurrentHitRuns = List.Count(List.Select(CurrentMonthData[AllIncidents], each _ <> null and Text.Contains(_, "Hit"))),
    PrevHitRuns = List.Count(List.Select(PrevMonthData[AllIncidents], each _ <> null and Text.Contains(_, "Hit"))),
    HitRunChange = try (CurrentHitRuns - PrevHitRuns) / PrevHitRuns otherwise 0,
    
    // 4. ENHANCED PLATOON PERFORMANCE (A/B/Traffic) - Fixed with null checks
    PlatoonA_Cases = List.Count(List.Select(CurrentMonthData[Platoon], each _ <> null and _ = "A")),
    PlatoonB_Cases = List.Count(List.Select(CurrentMonthData[Platoon], each _ <> null and _ = "B")),
    Traffic_Cases = List.Count(List.Select(CurrentMonthData[Squad], each _ <> null and _ = "TFR")),
    PlatoonSummary = "A:" & Text.From(PlatoonA_Cases) & " | B:" & Text.From(PlatoonB_Cases) & " | Traffic:" & Text.From(Traffic_Cases),
    
    // 5. RUSH HOUR IMPACT (6-9 AM and 3-6 PM on Weekdays) - Fixed with null checks
    RushHourCrashes = List.Count(List.Select(CurrentMonthData[IsRushHour], each _ <> null and _ = true)),
    RushHourRate = if CurrentMVAs > 0 then RushHourCrashes / CurrentMVAs else 0,
    
    // 6. TIME OF DAY BREAKDOWN - Fixed with null checks
    MorningPeak = List.Count(List.Select(CurrentMonthData[TimeOfDay], each _ <> null and _ = "Morning Peak (08:00–11:59)")),
    EveningPeak = List.Count(List.Select(CurrentMonthData[TimeOfDay], each _ <> null and _ = "Evening Peak (16:00–19:59)")),
    TimeBreakdown = "Morning Peak: " & Text.From(MorningPeak) & " | Evening Peak: " & Text.From(EveningPeak),
    
    // 7. CASE CLOSURE PERFORMANCE (Traffic Only) - Fixed with null checks
    TrafficCases = Table.SelectRows(CurrentMonthData, each [Squad] <> null and [Squad] = "TFR"),
    TrafficSupplements = Table.SelectRows(TrafficCases, each [IsSupplement] <> null and [IsSupplement] = true),
    ClosedCases = List.Count(List.Select(TrafficSupplements[FinalCaseStatus], each _ <> null and _ <> "Open" and _ <> "Case_Status")),
    ClosureRate = if Table.RowCount(TrafficSupplements) > 0 then ClosedCases / Table.RowCount(TrafficSupplements) else 0,
    
    // 8. TOP CRASH LOCATIONS - Fixed with null checks
    LocationAnalysis = Table.Group(
        Table.SelectRows(CurrentMonthData, each [Block] <> null), 
        {"Block"}, 
        {{"CrashCount", each Table.RowCount(_), Int64.Type}}
    ),
    TopLocation = Table.Top(Table.Sort(LocationAnalysis, {{"CrashCount", Order.Descending}}), 1),
    HotspotLocation = if Table.RowCount(TopLocation) > 0 then TopLocation{0}[Block] else "No Data",
    HotspotCount = if Table.RowCount(TopLocation) > 0 then TopLocation{0}[CrashCount] else 0,
    
    // === EXECUTIVE SUMMARY TABLE ===
    SummaryTable = #table(
        type table [Metric = text, Current_Month = any, Previous_Month = any, Change_Percent = number, Status = text],
        {
            {"Total MVAs", CurrentMVAs, PrevMVAs, MVAChange, if MVAChange > 0 then "↑ Increase" else "↓ Decrease"},
            {"Injury Crashes", CurrentInjuries, PrevInjuries, InjuryChange, if InjuryChange > 0 then "⚠️ Increase" else "✅ Decrease"},
            {"Hit-and-Runs", CurrentHitRuns, PrevHitRuns, HitRunChange, if HitRunChange > 0 then "⚠️ Increase" else "✅ Decrease"},
            {"Rush Hour Rate (6-9 AM, 3-6 PM)", Text.From(Number.Round(RushHourRate * 100, 1)) & "%", "", null, if RushHourRate > 0.3 then "⚠️ High" else "✅ Normal"},
            {"Time Patterns", TimeBreakdown, "", null, "ℹ️ Info"},
            {"Traffic Closure Rate", Text.From(Number.Round(ClosureRate * 100, 1)) & "%", "", null, if ClosureRate > 0.8 then "✅ Good" else "⚠️ Needs Attention"},
            {"Unit Deployment", PlatoonSummary, "", null, "ℹ️ Info"},
            {"Top Crash Location", HotspotLocation & " (" & Text.From(HotspotCount) & ")", "", null, if HotspotCount > 5 then "⚠️ Hotspot" else "✅ Normal"}
        }
    )
in
    SummaryTable

