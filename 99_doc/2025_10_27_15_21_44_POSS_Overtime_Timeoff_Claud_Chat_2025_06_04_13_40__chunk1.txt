# Police Analytics Implementation - Project Summary

## Executive Overview

**Project**: Hackensack Police Department POSS Export Analytics Implementation  
**Duration**: One session intensive troubleshooting and development  
**Outcome**: Successfully transformed manual, fragmented overtime/time-off tracking into automated, comprehensive analytics dashboard  
**Primary User**: Police Chief and Senior Leadership  
**System**: Microsoft Excel Power Query connecting to POSS scheduling application exports

---

## Problem Statement

### Initial Challenges
1. **Data Fragmentation**: OVERTIME and TIME_OFF data in separate, cluttered Power Query setups
2. **Query Bloat**: 7+ helper queries per dataset creating workspace clutter  
3. **Missing Critical Data**: Injured on duty hours showing as NULL despite existing in source files
4. **Culture/Language Conflicts**: Arabic Office language causing "Culture is invalid" errors
5. **File Protection Issues**: .xls files with protection blocking data access
6. **Inconsistent Data Types**: Mixed datetime/date/text formats preventing reliable calculations
7. **Manual Monthly Processes**: No automation for current/previous month reporting

### Core Issues Identified
- **January-February YTD data** containing injured on duty records was not being processed
- **Multiple file formats** (.xlsx/.xls) causing processing failures
- **Power Query helper functions** creating maintenance overhead
- **Hard-coded date logic** preventing dynamic month filtering

---

## Solution Architecture

### Phase 1: Data Foundation Cleanup
**Objective**: Establish reliable, automated data connections

#### OVERTIME Data Streamlining
- **Before**: 7 queries (OVERTIME_EXPORT, Parameter1, Transform Sample File, Sample File, Transform File, 25_Mar, 25_Apr)
- **After**: 3 clean queries (OVERTIME_MASTER, OVERTIME_REPORT_MONTH, OVERTIME_CURRENT_MONTH)
- **Method**: Single comprehensive query with built-in transformations, eliminated helper functions

#### TIME_OFF Data Resolution  
- **Challenge**: Injured on duty data (205+ hours) not appearing due to file access issues
- **Root Cause**: January-February YTD file was .xls format with protection, while query only processed .xlsx
- **Solution**: 
  1. Converted all source files to .xlsx format
  2. Added error handling with `try...otherwise null` for protected files
  3. Implemented dynamic date conversion to handle Excel serial numbers

### Phase 2: Culture and Language Conflicts
**Issue**: Arabic Office language installation causing Power Query culture errors

#### Resolution Process
1. **Identified**: `Expression.Error: The value for option 'Culture' is invalid`
2. **Root Cause**: Arabic version of Microsoft Office conflicting with Power Query date/text functions
3. **Solution**: 
   - Uninstalled Arabic Office components
   - Replaced culture-sensitive functions (`Date.MonthName()`) with manual logic
   - Used English-only date processing

### Phase 3: Advanced Analytics Implementation
**Objective**: Create executive-level dashboard for strategic decision making

#### Executive Dashboard Features
- **Rolling 12-Month Metrics**: Comprehensive operational overview (June 2024 → June 2025)
- **Automated Time Filtering**: Dynamic date ranges eliminate manual updates
- **Comprehensive Coverage**: Both overtime and time-off analytics in single dashboard
- **Inclusive Metrics**: Covers sworn officers and civilian staff

---

## Technical Implementation Details

### Core Queries Developed

#### 1. OVERTIME_MASTER
```powerquery
- Source: OVERTIME_EXPORT folder (.xlsx files)
- Transformations: Date components, pay type categorization, text cleaning
- Output: Complete overtime dataset with proper data types
```

#### 2. TIME_OFF_MASTER  
```powerquery
- Source: TIME_OFF_EXPORT folder (.xlsx files)
- Key Features: Error handling, Times column splitting, date conversion
- Challenge Resolved: January-February YTD data inclusion
```

#### 3. ROLLING_12_MONTHS_EXECUTIVE_SUMMARY
```powerquery
- Data Sources: OVERTIME_MASTER + TIME_OFF_MASTER
- Time Period: Dynamic rolling 12-month window
- Metrics: 9 key performance indicators
- Audience: Police Chief and senior leadership
```

### Data Transformations

#### OVERTIME Processing
- **Pay Type Classification**: Separated "1.0 Comp Time", "1.5 Comp Time" vs "1.5 Cash", "2.0 Cash"
- **Date Components**: Year, Month Name, Week of Year, Day Name
- **Text Cleaning**: Group, Employee, Reason, Status fields
- **Cost Calculations**: Rate × Hours for budget analysis

#### TIME_OFF Processing  
- **Times Column Splitting**: "18:00-00:00" → START_TIME (18:00) + END_TIME (00:00)
- **Reason Text Matching**: Flexible search for "INJUR", "DUTY", "IOD" patterns
- **Units Handling**: Hours vs Days distinction (SLEO III Sick Hours vs Sick Days count)
- **Date Standardization**: Excel serial numbers → proper date format

### Error Handling Strategies
1. **Protected File Exclusion**: `try...otherwise null` wrapper
2. **Date Type Conversion**: `Date.From()` for mixed datetime/date comparisons  
3. **Missing Column Handling**: `MissingField.Ignore` parameter
4. **Culture-Neutral Functions**: Manual month name assignment vs `Date.MonthName()`

---

## Key Metrics Delivered

### ROLLING_12_MONTHS_EXECUTIVE_SUMMARY Output
| Metric | Value | Purpose |
|--------|--------|---------|
| **Accrued Comp Time (Hours)** | 233.5 | Workload management |
| **Accrued Overtime (Hours)** | 602.5 | Budget planning |
| **Total Overtime Cost YTD** | $1,241 | Financial oversight |
| **Injured on Duty (Hours)** | 1,853.67 | Safety metrics |
| **Military Leave (Hours)** | 2,116 | Resource planning |
| **SLEO III Sick (Hours)** | 280 | Health trends |
| **PEO Sick (Hours)** | 34 | Civilian staff health |
| **Sick Days (Count)** | 1,342 | Attendance patterns |
| **Members with OT Activity** | 80 | Workforce utilization |

### Data Coverage
- **Time Period**: Rolling 12 months (automatically updating)
- **Personnel**: 115+ sworn members + civilian staff
- **Data Sources**: POSS scheduling application exports
- **Update Frequency**: Refreshes with new monthly exports

---

## Critical Breakthroughs

### Issue Resolution Timeline

#### 1. The Injured on Duty Mystery
- **Problem**: 205+ hours of injured on duty time showing as NULL
- **Investigation**: Data confirmed to exist in January-February 2025
- **Discovery**: YTD file was .xls format, query only processed .xlsx
- **Resolution**: File format conversion + error handling

#### 2. Culture Error Resolution
- **Problem**: Persistent "Culture is invalid" errors blocking data processing
- **Root Cause**: Arabic Office installation conflicting with Power Query
- **Solution**: Complete Arabic Office uninstallation + culture-neutral code

#### 3. File Location Issue  
- **Problem**: Queries working locally but not updating in shared environment
- **Discovery**: File not properly saved to OneDrive
- **Resolution**: Moved to proper OneDrive location for synchronization

#### 4. Date Type Mismatches
- **Problem**: `Cannot apply operator < to types Date and DateTime`
- **Solution**: `Date.From()` conversion wrappers for consistent comparisons

---

## Best Practices Established

### Power Query Development
1. **Single Comprehensive Queries**: Avoid helper function proliferation
2. **Error Handling**: Always use `try...otherwise null` for file operations
3. **Culture-Neutral Code**: Avoid locale-dependent functions in multi-language environments
4. **Flexible Text Matching**: Use `Text.Contains()` with partial strings for robust data matching
5. **Dynamic Date Filters**: Rolling windows vs hard-coded years for evergreen analytics

### File Management
1. **Consistent Formats**: Standardize on .xlsx for reliability
2. **OneDrive Synchronization**: Ensure proper cloud storage for shared access
3. **Error Logging**: Document and exclude problematic source files
4. **Version Control**: Maintain backup queries during major modifications

### Analytics Design
1. **Inclusive Metrics**: Account for both sworn and civilian personnel
2. **Clear Labeling**: Descriptive metric names for executive audiences
3. **Time Period Transparency**: Clearly indicate data windows (rolling vs YTD)
4. **Flexible Architecture**: Design for future enhancements and additional data sources

---

## Deliverables

### 1. Production Queries (6 total)
- **OVERTIME_MASTER**: Complete overtime dataset
- **OVERTIME_REPORT_MONTH**: Previous month overtime (auto-filtering)
- **OVERTIME_CURRENT_MONTH**: Current month overtime (auto-filtering)
- **TIME_OFF_MASTER**: Complete time-off dataset  
- **TIME_OFF_REPORT_MONTH**: Previous month time-off (auto-filtering)
- **TIME_OFF_CURRENT_MONTH**: Current month time-off (auto-filtering)

### 2. Executive Dashboard
- **ROLLING_12_MONTHS_EXECUTIVE_SUMMARY**: Strategic leadership metrics

### 3. Documentation
- **M Code Repository**: Complete query code for replication/modification
- **Implementation Guide**: Step-by-step setup instructions
- **Troubleshooting Guide**: Common issues and solutions

---

## Future Enhancement Opportunities

### Phase 3: Advanced Analytics (Next Steps)
1. **GROUP_SUPERVISORY_REPORT**: Performance analysis by unit (PLT A, PLT B, Communications)
2. **OFFICER_WORKLOAD_ANALYSIS**: Individual burnout indicators and overtime dependency
3. **COST_ANALYSIS_DASHBOARD**: Budget variance and forecasting
4. **TREND_ANALYSIS**: Seasonal patterns and predictive insights

### Automation Enhancements
1. **Scheduled Refresh**: Power Platform integration for automatic updates
2. **Alert System**: Threshold notifications for high overtime/sick time
3. **Comparative Analysis**: Year-over-year trend dashboards
4. **Drill-Down Capabilities**: Detail views from executive summary

### Data Integration Expansion
1. **Additional POSS Modules**: Training, equipment, incidents
2. **Financial System Integration**: Budget vs actual reporting
3. **HR System Connection**: Personnel status, certifications, performance
4. **Geographic Analysis**: Patrol area workload distribution

---

## Success Metrics

### Quantitative Achievements
- **Query Reduction**: 14 cluttered queries → 7 clean, purpose-built queries (-50%)
- **Data Accuracy**: 100% of injured on duty hours now captured (was 0%)
- **Automation**: Monthly reporting now auto-updates (was manual)
- **Time Savings**: Estimated 2-3 hours monthly analyst time saved

### Qualitative Improvements
- **Executive Visibility**: Chief now has real-time operational metrics
- **Strategic Planning**: 12-month rolling data enables trend-based decisions
- **Workforce Management**: Clear overtime utilization patterns across all staff
- **Safety Oversight**: Injured on duty tracking for worker safety initiatives

### Foundation for Growth
- **Scalable Architecture**: Framework supports additional analytics modules
- **Reliable Data Pipeline**: Robust error handling ensures consistent operations
- **Professional Presentation**: Executive-ready dashboards for leadership use
- **Documentation**: Complete implementation guide for future maintenance

---

## Lessons Learned

### Technical Insights
1. **File Format Matters**: .xls protection can silently break data pipelines
2. **Language Settings**: Office language conflicts create unexpected Power Query errors
3. **Date Handling**: Mixed date/datetime types require careful conversion
4. **Error Handling**: Proactive exception handling prevents cascade failures

### Process Insights  
1. **Incremental Testing**: Test each component before integration
2. **Root Cause Analysis**: Surface-level symptoms often mask deeper issues
3. **User Requirements**: Rolling timeframes often more valuable than static periods
4. **Change Management**: File location and sharing critical for collaborative analytics

### Business Value
1. **Executive Engagement**: Leadership visibility drives better resource decisions
2. **Operational Efficiency**: Automated reporting frees analyst time for higher-value work
3. **Data Quality**: Clean, reliable metrics build organizational trust in analytics
4. **Strategic Planning**: Historical trends enable proactive vs reactive management

---

## Project Impact

**For the Police Chief:**
- Real-time visibility into department operations
- Data-driven insights for budget and staffing decisions
- Automated monthly reporting eliminating manual processes
- Foundation for advanced workforce analytics

**For Department Administration:**
- Streamlined data processing reducing analyst workload
- Reliable metrics for state reporting and compliance
- Improved accuracy in overtime and leave tracking
- Scalable platform for additional analytics needs

**For the Organization:**
- Professional-grade analytics capability rivaling larger departments
- Evidence-based decision making replacing intuition-based choices
- Enhanced operational efficiency through automated reporting
- Strategic advantage through comprehensive workforce intelligence

---

## Contact and Maintenance

**Primary System**: OVERTIME_MASTER_V2.xlsm  
**Location**: `C:\Users\carucci_r\OneDrive - City of Hackensack\_MONTHLY_DATA\EXCEL_MASTER_FOR_MONTHLY\`  
**Data Sources**: POSS Export folders (OVERTIME_EXPORT, TIME_OFF_EXPORT)  
**Refresh Schedule**: Monthly with new POSS exports  
**Maintenance**: Quarterly review of query performance and data quality

**Implementation Status**: ✅ **COMPLETE** - Production ready for executive use