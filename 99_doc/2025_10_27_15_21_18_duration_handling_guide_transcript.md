# Duration Handling Guide

**Processing Date:** 2025-10-27 15:21:18
**Source File:** duration_handling_guide.md
**Total Chunks:** 1

---

# 🕒 2025-06-08-15-30-00
# Response_Time_Calculator/Duration_Handling_Guide.md
# Author: R. A. Carucci
# Purpose: Comprehensive guide for handling response times, durations, and negative time calculations in CAD/RMS data

# Response Time & Duration Handling Guide

## 🎯 Core Principles

### **1. Always Handle Negative Durations**
- **Problem**: CAD systems sometimes record timestamps out of order
- **Solution**: Detect negative durations and flip them automatically
- **Logic**: If `TimeOut - TimeDispatched < 0`, use `TimeDispatched - TimeOut`

### **2. Apply Realistic Bounds**
- **Response Time**: 0-60 minutes (anything beyond indicates data error)
- **Time on Scene**: 0-12 hours (720 minutes max)
- **Flag extreme values** for supervisory review

### **3. Categorize for Analysis**
- **Response Categories**: Instant, Very Fast, Fast, Normal, Slow, Very Slow
- **Scene Categories**: No Time, Brief, Normal, Extended, Very Long
- **Performance Levels**: Excellent, Good, Acceptable, Needs Improvement

## 🔧 Implementation Steps

### **Step 1: Raw Duration Calculation**
```m
AddResponseTime = Table.AddColumn(Source, "ResponseTime_Raw", each 
    try 
        let 
            dispatched = [TimeDispatched],
            arrived = [TimeOut],
            normalDuration = arrived - dispatched,
            // Handle negative durations by flipping
            correctedDuration = if normalDuration < #duration(0,0,0,0) 
                              then dispatched - arrived 
                              else normalDuration
        in correctedDuration
    otherwise null, 
type duration)
```

### **Step 2: Bounds Checking**
```m
AddResponseTimeMin = Table.AddColumn(Source, "ResponseTime_Minutes", each 
    let rawMinutes = try Duration.TotalMinutes([ResponseTime_Raw]) otherwise null
    in if rawMinutes <> null and rawMinutes >= 0 and rawMinutes <= 60 
       then Number.Round(rawMinutes, 2) 
       else null, 
type number)
```

### **Step 3: Outlier Detection**
```m
AddOutlierFlags = Table.AddColumn(Source, "IsOutlier", each 
    let rt = [ResponseTime_Minutes], toc = [TimeOnScene_Minutes]
    in (rt <> null and rt > 10) or (toc <> null and toc > 120) or
       (rt <> null and rt < 0.5), 
type logical)
```

## 🚩 Key Flag Columns to Include

### **1. IsOutlier (Boolean)**
- **Purpose**: Quick filter for supervisory review
- **Criteria**: Response > 10 min OR Scene > 2 hrs OR Response < 30 sec

### **2. OutlierReason (Text)**
- **Purpose**: Detailed explanation of why record is flagged
- **Examples**: 
  - "Slow Response (>12.3 min)"
  - "Extended Scene Time (>3.2 hrs)"
  - "Suspiciously Fast Response (<30 sec)"

### **3. DataQuality_Flag (Text)**
- **Purpose**: Identify data entry errors
- **Values**: 
  - `NEGATIVE_RESPONSE_TIME`
  - `NEGATIVE_SCENE_TIME`
  - `EXTREME_RESPONSE`
  - `EXTREME_SCENE`
  - `RESPONSE_CALC_ERROR`

### **4. Performance_Level (Text)**
- **Purpose**: Executive reporting and trending
- **Categories**: Excellent (≤3 min), Good (≤5 min), Acceptable (≤8 min), Needs Improvement (>8 min)

## ⚠️ Common Pitfalls & Solutions

### **Problem 1: Negative Response Times**
- **Cause**: Timestamps recorded out of sequence
- **Solution**: Automatic duration flipping logic
- **Flag**: Mark as `NEGATIVE_RESPONSE_TIME` for manual review

### **Problem 2: Zero Duration Times**
- **Cause**: Simultaneous timestamp entry or system glitches
- **Solution**: Categorize as "Instant" but flag for review
- **Logic**: `if rt = 0 then "Instant (0 min)"`

### **Problem 3: Extreme Values**
- **Cause**: Data entry errors, system crashes, or actual incidents
- **Solution**: Set realistic upper bounds and flag extremes
- **Bounds**: Response (60 min), Scene (12 hours)

### **Problem 4: Missing Timestamps**
- **Cause**: Incomplete data entry or system issues
- **Solution**: Handle nulls gracefully and flag missing data
- **Logic**: `if rt = null and toc = null then "Missing Time Data"`

## 📊 Recommended Analysis Queries

### **Executive Summary Query**
```m
ExecutiveSummary = Table.Group(FilteredData, {"ReportPeriod"}, {
    {"Total_Calls", each Table.RowCount(_), Int64.Type},
    {"Avg_Response_Min", each List.Average(List.RemoveNulls([ResponseTime_Minutes])), type number},
    {"Calls_Over_5Min", each List.Count(List.Select([ResponseTime_Minutes], each _ > 5)), Int64.Type},
    {"Outlier_Count", each List.Count(List.Select([IsOutlier], each _ = true)), Int64.Type},
    {"Data_Quality_Issues", each List.Count(List.Select([DataQuality_Flag], each _ <> null)), Int64.Type}
})
```

### **QA Review Query**
```m
QAReview = Table.SelectRows(ProcessedData, each 
    [IsOutlier] = true or [DataQuality_Flag] <> null
)
```

## 🎯 Best Practices

### **1. Always Validate Before Analysis**
- Check for negative durations first
- Apply bounds checking consistently
- Flag obvious data errors

### **2. Document Your Logic**
- Include comments explaining duration calculations
- Note any department-specific adjustments
- Document outlier thresholds and reasoning

### **3. Create Multiple Time Views**
- Raw durations (for debugging)
- Cleaned minutes (for analysis)  
- Categories (for reporting)
- Performance levels (for executives)

### **4. Regular Quality Audits**
- Review flagged records monthly
- Adjust outlier thresholds based on operational reality
- Train staff on proper timestamp entry

## 🔄 Integration Tips

### **For Power BI Reports**
- Use Performance_Level for executive dashboards
- Create time-series charts using cleaned minutes
- Build alert tables from outlier flags

### **For Excel Analysis**  
- Export flagged records for supervisor review
- Use categories for pivot table grouping
- Create conditional formatting based on flags

### **For Database Storage**
- Store both raw and cleaned values
- Index on flag columns for quick filtering
- Archive extreme outliers after review

## 📈 Success Metrics

- **Data Quality**: < 5% of records flagged as outliers
- **Response Performance**: 80% of calls < 5 minutes response
- **Completeness**: < 2% missing timestamp data
- **Consistency**: Stable month-over-month averages

I've created two comprehensive artifacts for you:

## 📋 What You've Got:

### **1. Complete M Code Module** 
- **Robust duration calculations** with automatic negative handling
- **Comprehensive outlier detection** with detailed reasons
- **Multiple flag columns** for different analysis needs
- **Performance categorization** for executive reporting

### **2. Implementation Guide**
- **Step-by-step instructions** for each calculation
- **Common pitfalls** and how to avoid them
- **Best practices** for data quality management
- **Integration tips** for Power BI, Excel, and databases

## 🎯 Key Features:

**✅ Handles Negative Times**: Automatically flips reversed timestamps
**✅ Bounds Checking**: Filters unrealistic values (Response: 0-60 min, Scene: 0-12 hrs)
**✅ Multiple Flag Columns**: 
- `IsOutlier` (boolean for quick filtering)
- `OutlierReason` (detailed explanations)
- `DataQuality_Flag` (data entry error detection)
- `Performance_Level` (executive reporting categories)

**✅ Comprehensive Categories**: From "Instant" to "Extreme" with specific thresholds

## 🚀 How to Use:

1. **Replace `YourTableName`** with your actual table/query name
2. **Adjust column names** to match your schema (TimeDispatched, TimeOut, TimeIn)
3. **Customize thresholds** based on your department's standards
4. **Add to any project** dealing with CAD/RMS response time analysis

The code is completely portable and includes all the lessons learned from your T4 project. Perfect for sharing with other analysts or departments! **Need any adjustments to the thresholds or additional flag conditions? **

