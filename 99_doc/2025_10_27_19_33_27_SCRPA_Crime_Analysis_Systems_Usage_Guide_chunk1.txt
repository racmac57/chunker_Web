# SCRPA Crime Analysis Systems - Usage Guide

## 🎯 Usage Examples:

### Original Multi-Period System

#### Quick Weekly Report:
```bash
# Type: soriginal
# Expands to full command with today's date
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "...\crime_report_tool\main.py" true true false 30 false 2025_06_10
```

#### Manual Command Building:
```bash
# Step 1: Type spath
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"

# Step 2: Add space, then type sscript
"...\crime_report_tool\main.py"

# Step 3: Add parameters manually
true true false 30 false 2025_06_10
```

#### Custom Parameter Examples:
```bash
# Maps only (no charts)
spath sscript true false false 30 false 2025_06_10

# Charts only (no maps)  
spath sscript false true false 30 false 2025_06_10

# Dry run test
spath sscript true true false 30 true 2025_06_10
```

### 7-Day Focused System

#### Quick Weekly Report:
```bash
# Type: s7day
# Expands to full command with today's date
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "...\7_day_crime_report_tool_scripts\main.py" true true false 30 false 2025_06_10
```

#### Manual Command Building:
```bash
# Step 1: Type s7path (or spath - same path)
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"

# Step 2: Add space, then type s7script
"...\7_day_crime_report_tool_scripts\main.py"

# Step 3: Add parameters manually
true true false 30 false 2025_06_10
```

#### Weekly Date Examples:
```bash
# June 10, 2025 report
s7day → ...false 2025_06_10

# June 17, 2025 report
s7day → ...false 2025_06_17

# June 24, 2025 report
s7day → ...false 2025_06_24
```

---

## 🔄 System Comparison:

### Original Multi-Period System
- **TextExpander**: `soriginal`
- **Script Path**: `crime_report_tool\main.py`
- **Project File**: `TimeSCRPATemplet.aprx`

#### Output Structure:
```
C05W23_2025_06_03/
├── MV_Theft_Map.png (7-Day + 28-Day + YTD overlay)
├── MV_Theft_Chart.png (grouped bars: 7-Day, 28-Day, YTD)
├── Burglary_Auto_Map.png (multi-period heat map)
├── Burglary_Auto_Chart.png (all periods)
├── [etc...]
└── processing_summary.txt
```

#### Map Characteristics:
- **Layer Visibility**: All three periods visible simultaneously
- **Transparency**: 7-Day (0%), 28-Day (30%), YTD (60%)
- **Heat Map Style**: Multi-layer overlay showing temporal progression
- **Legend**: Shows all three periods

#### Use Cases:
- ✅ **Comprehensive trend analysis**
- ✅ **Pattern identification across time periods**
- ✅ **Internal departmental analysis**
- ✅ **Statistical reporting**

---

### 7-Day Focused System
- **TextExpander**: `s7day`
- **Script Path**: `7_day_crime_report_tool_scripts\main.py`
- **Project File**: `7_Day_Templet_SCRPA_Time.aprx`

#### Output Structure:
```
C05W23_2025_06_03_7Day/
├── MV_Theft/
│   ├── MV_Theft_Map.png (7-Day only OR placeholder)
│   └── MV_Theft_Chart.png (grouped bars: 7-Day, 28-Day, YTD)
├── Burglary_Auto/
│   ├── Burglary_Auto_Map.png (7-Day only OR placeholder)
│   └── Burglary_Auto_Chart.png (all periods)
├── [etc...]
```

#### Map Characteristics:
- **Layer Visibility**: Only 7-Day period visible
- **Transparency**: Single layer at 0% (full opacity)
- **Heat Map Style**: Clean, single-period incidents only
- **Placeholders**: Auto-generated for zero-incident crime types
- **Legend**: Shows only 7-Day period

#### Use Cases:
- ✅ **Weekly executive briefings**
- ✅ **External stakeholder reports**
- ✅ **Clean incident-specific visualization**
- ✅ **Recipient-specific requirements**

---

### Decision Matrix:

| Need | Original System | 7-Day System |
|------|----------------|--------------|
| **Multi-period analysis** | ✅ Perfect | ❌ Charts only |
| **Clean 7-day focus** | ❌ Cluttered | ✅ Perfect |
| **Zero-incident handling** | 🔶 Empty maps | ✅ Placeholders |
| **File organization** | 🔶 Flat structure | ✅ Subfolders |
| **Executive reporting** | 🔶 Too complex | ✅ Ideal |
| **Trend analysis** | ✅ Excellent | 🔶 Limited |

### Quick Selection Guide:
- **Use `soriginal`** for: Internal analysis, trend identification, comprehensive reporting
- **Use `s7day`** for: Weekly briefings, external reports, incident-specific focus

Both systems preserve charts with all time periods for temporal analysis while offering different map visualization approaches.