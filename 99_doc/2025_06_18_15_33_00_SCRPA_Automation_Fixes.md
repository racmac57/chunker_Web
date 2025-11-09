Below, I’ve updated the documentation to incorporate the provided checklist and additional details, ensuring all requirements are met, including version control, insight tagging, JSON export, and a quick access index. The Markdown filename includes a timestamp reflecting the current date and time (2025-06-18 16:41:00 EDT). The checklist of accomplished tasks and pending improvements has been integrated into the documentation, along with suggested enhancements.
A. Updated Markdown Documentation
Filename: 2025_06_18_16_41_00_SCRPA_Automation_Fixes.md
markdown
---
Title: SCRPA Report Automation Debugging and Chart Export
Date: 2025-06-18
Participants: RAC, ChatGPT
Chat Name: SCRPA Report Automation Fixes
Tags: ArcPy, Python, GIS, Chart Export, Error Handling, Chart Formatting, ArcPy Debugging, Folder Management, Logging, SQL Patterns, Layer Mapping, Chart Automation
Source: Chat
---

# SCRPA Report Automation Debugging and Chart Export

**Keyword Index**: ArcPy, chart_export, import error, SQL query, layer mismatch, logging, matplotlib, PowerPoint templates, batch file, folder structure, error handling, chart formatting, ArcPy debugging, folder management, SQL patterns, layer mapping, chart automation

## Summary
This conversation resolved errors in an ArcGIS Pro Python script for generating crime report charts (7-Day, 28-Day, YTD periods). Issues included `ImportError`, missing PowerPoint templates, layer mismatches, and SQL pattern errors causing missing data bars for "Motor Vehicle Theft" and "Burglary Auto". Fixes updated `chart_export.py` and `config.py`, added layer name mapping, improved SQL patterns, and added debug logging. The script now generates bar charts with proper data, labels, and folder structure. A checklist tracks completed tasks and pending improvements.

## Changelog
### [1.2] - 2025-06-18
#### Added
- `config.py`: Added `LAYER_NAME_MAP` for mapping logical crime types to ArcGIS layer names (CODE_20250618_003).
- `config.py`: Updated `get_sql_pattern_for_crime` to support list-based patterns for partial calltype matches (e.g., "Burglary - Commercial - 2C:18-2").
#### Changed
- `chart_export.py`: Updated layer name lookup to use `LAYER_NAME_MAP` (CODE_20250618_002).
- `chart_export.py`: Enhanced SQL logging for debugging missing data bars.

### [1.1] - 2025-06-18
#### Changed
- `chart_export.py`: Added case-insensitive layer matching (CODE_20250618_002).
- `chart_export.py`: Improved y-axis padding for label visibility.
- `chart_export.py`: Added logging for SQL and layer names.

### [1.0] - 2025-06-18
#### Added
- `chart_export.py`: Initial version with embedded data collection (CODE_20250618_001).
- `main.py`: Updated to use `generate_chart`.
- Created required folders and PowerPoint templates.

## Import Error: `export_chart` Not Found
### 🔴 Broken Code
```python
# main.py
# Code ID: CODE_20250618_001_BROKEN
# Version: v0.1
# 🕒 2025-06-18 15:29:00
from chart_export import export_chart
success = export_chart(crime_type)
🛠 Issue Description
main.py tried to import export_chart, but chart_export.py only defined generate_chart.
💡 Suggestions/Fixes
Add export_chart wrapper in chart_export.py.
Update main.py to use generate_chart directly.
🟢 Working Code (CODE_20250618_001)
python
# chart_export.py
# Author: R. A. Carucci
# Purpose: Generate combined 7-Day, 28-Day, and YTD time-of-day bar chart for crime type.
# Code ID: CODE_20250618_001
# Version: v1.0
# 🕒 2025-06-18 15:29:00
[Full chart_export.py content as provided previously]
Missing PowerPoint Templates
🔴 Broken Code
python
# config.py
# Code ID: CODE_20250618_002_BROKEN
# Version: v0.1
# 🕒 2025-06-18 15:29:00
raise FileNotFoundError(f"Missing required paths: {missing}")
🛠 Issue Description
config.py expected a reports folder and three .pptx templates that didn’t exist.
💡 Suggestions/Fixes
Create C:\Users\carucci_r\OneDrive - City of Hackensack\_Hackensack_Data_Repository\GIS_Tools\SCRPA_Reports.
Add blank SCRPA_7Day_Template.pptx, SCRPA_28Day_Template.pptx, SCRPA_YTD_Template.pptx in C:\Templates\.
🟢 Working Code
No code changes needed; folder and files created manually.
Missing 7-Day Incident Data
🔴 Broken Code
python
# chart_export.py
# Code ID: CODE_20250618_003_BROKEN
# Version: v0.1
# 🕒 2025-06-18 15:29:00
lyr = next((l for l in map_obj.listLayers() if l.name == layer_name), None)
🛠 Issue Description
The 7-Day layer wasn’t found due to a naming mismatch (e.g., "Robbery 7-Day" vs. "Robbery 7Day").
💡 Suggestions/Fixes
Use case-insensitive layer matching.
Add logging for layer names and SQL queries.
🟢 Working Code (CODE_20250618_002)
python
# chart_export.py
# Author: R. A. Carucci
# Purpose: Debug layer matching and SQL for crime charts
# Code ID: CODE_20250618_002
# Version: v1.1
# 🕒 2025-06-18 15:29:00
lyr = next((l for l in map_obj.listLayers() if l.name.lower() == layer_name.lower()), None)
logging.info(f"🔎 Looking for layer: {layer_name}")
logging.info(f"🗓️ {period} SQL: {sql}")
Missing Data Bars: Motor Vehicle Theft and Burglary Auto
🔴 Broken Code
python
# config.py
# Code ID: CODE_20250618_004_BROKEN
# Version: v1.1
# 🕒 2025-06-18 16:33:00
def get_sql_pattern_for_crime(crime_type):
    patterns = {
        "Motor Vehicle Theft": "Motor Vehicle Theft",
        "Burglary Auto": "Burglary - Auto",
        # ...
    }
    return patterns.get(crime_type)
🛠 Issue Description
Charts for "Motor Vehicle Theft" and "Burglary Auto" showed no data bars due to mismatched SQL patterns. The calltype field contained values like "Motor Vehicle Theft - 2C:20-3", requiring partial matches with LIKE '%pattern%'.
💡 Suggestions/Fixes
Update get_sql_pattern_for_crime to return lists for partial matches.
Add LAYER_NAME_MAP in config.py for layer name mapping.
Modify chart_export.py to use LAYER_NAME_MAP.
🟢 Working Code (CODE_20250618_003)
python
# config.py
# Author: R. A. Carucci
# Purpose: Centralized configuration for SCRPA report automation.
# Code ID: CODE_20250618_003
# Version: v1.2
# 🕒 2025-06-18 16:33:00

import os
from datetime import timedelta

CRIME_TYPES = [
    "Motor Vehicle Theft",
    "Burglary Auto",
    "Burglary - Comm & Res",
    "Sexual Offenses",
    "Robbery"
]

LAYER_NAME_MAP = {
    "Motor Vehicle Theft": "MV Theft",
    "Burglary Auto": "Burglary - Auto",
    "Burglary - Comm & Res": "Burglary - Comm & Res",
    "Sexual Offenses": "Sexual Offenses",
    "Robbery": "Robbery"
}

def get_sql_pattern_for_crime(crime_type):
    patterns = {
        "Motor Vehicle Theft": ["Motor Vehicle Theft"],
        "Burglary Auto": ["Burglary - Auto"],
        "Burglary - Comm & Res": ["Burglary - Residence", "Burglary - Commercial"],
        "Sexual Offenses": ["Sexual"],
        "Robbery": ["Robbery"]
    }
    return patterns.get(crime_type)

def get_7day_period_dates(report_date):
    return (report_date - timedelta(days=6), report_date)

def get_28day_period_dates(report_date):
    return (report_date - timedelta(days=27), report_date)

def get_ytd_period_dates(report_date):
    return (report_date.replace(month=1, day=1), report_date)

def get_crime_type_folder(crime_type, report_date_str):
    root = r"C:\Users\carucci_r\OneDrive - City of Hackensack\_Hackensack_Data_Repository\GIS_Tools\Scripts\ScriptsTimeSCRPATemplet\7_day_crime_report_tool_scripts\SCRPA_Reports"
    safe_name = crime_type.replace(" ", "_").replace("&", "And")
    return os.path.join(root, report_date_str, safe_name)
Rebuilding Charts: Detailed Instructions
Directory Structure
7_day_crime_report_tool_scripts/
├── chart_export.py
├── config.py
├── main.py
├── map_export.py
├── table_export.py
├── batch_chart_runner.py
├── report_packager.py
├── logger.py
├── run_scrpa_report.bat
├── README.md
└── SCRPA_Reports/  ← Output folder
Steps to Rebuild
Save config.py:
Copy the config.py code above into 7_day_crime_report_tool_scripts/config.py.
Ensure CRIME_TYPES, LAYER_NAME_MAP, and get_sql_pattern_for_crime are defined.
Update chart_export.py:
Replace the layer lookup in generate_combined_chart:
python
from config import LAYER_NAME_MAP
layer_prefix = LAYER_NAME_MAP.get(crime_type, crime_type)
layer_name = f"{layer_prefix} {period}"
Save as 7_day_crime_report_tool_scripts/chart_export.py.
Run Batch Export:
In ArcGIS Pro Python window, execute:
python
import sys
sys.path.append(r"C:\Users\carucci_r\OneDrive - City of Hackensack\_Hackensack_Data_Repository\GIS_Tools\Scripts\ScriptsTimeSCRPATemplet\7_day_crime_report_tool_scripts")
from chart_export import export_chart
from config import CRIME_TYPES
report_date = "2025_06_17"
for crime in CRIME_TYPES:
    print(f"📊 Exporting chart for: {crime}")
    try:
        export_chart(crime, report_date)
        print(f"✅ Chart exported: {crime}")
    except Exception as e:
        print(f"❌ Failed to export chart for {crime}: {e}")
Verify Output:
Charts are saved in SCRPA_Reports/YYYY_MM_DD/Crime_Type/Crime_Type_Cycle_TimeOfDay_Chart.png.
Check for data bars in all charts, especially "Motor Vehicle Theft" and "Burglary Auto".
Chart Features
Time Bins: Night (00:00–03:59), Early Morning (04:00–07:59), Morning (08:00–11:59), Afternoon (12:00–15:59), Evening (16:00–19:59), Late Evening (20:00–23:59).
Colors: 7-Day (#C2EABD), 28-Day (#E76F51), YTD (#9DADF2).
Labels: Inside bars, bold black text, white background, only for non-zero heights.
Y-Axis: Padded to 110% of max height for visibility.
SQL Patterns: Partial matches for calltype (e.g., LIKE '%Burglary - Commercial%').
Layer Mapping: Logical names mapped to ArcGIS layer names via LAYER_NAME_MAP.
Checklist: Accomplished and Pending Tasks
✅ Already Fixed / Working
Charts Render Properly for all listed CRIME_TYPES.
Correct Layer Mapping via LAYER_NAME_MAP.
Multi-pattern SQL support (e.g., "Burglary - Comm & Res" handles 2 patterns).
Bar Labeling Inside Bars with black font and white background.
X-Axis Orientation Fixed (horizontal time bins).
Chart Layout with spacing, scaling, and tight layout.
Automatic Folder Creation per crime type & report date.
All Charts Exported without error via export_chart().
🔧 Still To Fix / Improve
Issue
Description
Suggested Fix
Layer Missing Detection
Empty chart saved if layer doesn’t exist.
Add print(f"⚠️ No data layer for {crime_type} {period}").
Date Calculators
Assumed in memory, may fail if missing.
Ensure config.py includes get_7day_period_dates, etc.
Folder Overwrite Confirmation
Existing charts silently overwritten.
Add print(f"🔄 Overwriting {out_path}") or backup PNGs.
Optional CSV Export
No CSV with bin counts per period.
Implement CSV export for counts per bin.
Chart Title Wrapping
Long crime types may overflow title.
Use ax.set_title(..., wrap=True).
Documentation Storage
Setup not archived in .md or .txt.
Generate README_chart_export.md.
🧪 Optional Enhancements
Add unit tests using mock arcpy objects.
Add CLI script like python run_export.py --date 2025_06_17.
Add support for weekly auto-run via Task Scheduler.
🧠 Session Summary Token
SUMMARY_TOKEN_START
Date: 2025-06-18
Context: Debugged ArcGIS Pro script for crime report automation, fixing import errors, missing templates, layer mismatches, and SQL pattern errors.
Progress: Updated chart_export.py with layer mapping and logging; fixed config.py for SQL partial matches; created required folders/templates; documented checklist.
Pending: Implement CSV export, unit tests, PowerPoint embedding; address layer missing detection and title wrapping.
Tech: ArcPy, Python, matplotlib
AI: ChatGPT
Chat Name: SCRPA Report Automation Fixes
SUMMARY_TOKEN_END
🔍 Conversation Outline
✅ Topics Covered
Resolving ImportError for export_chart
Handling missing PowerPoint templates
Debugging missing 7-Day incident data
Fixing missing data bars for "Motor Vehicle Theft" and "Burglary Auto"
Adding logging for SQL and layer visibility
Adjusting chart labels and y-axis padding
Mapping logical crime types to ArcGIS layer names
Updating SQL patterns for partial calltype matches
Documenting checklist of accomplished and pending tasks
🧠 Final Working Code(s)
CODE_20250618_001: chart_export.py with embedded data collection (v1.0)
CODE_20250618_002: Updated chart_export.py with case-insensitive layer matching and debug logging (v1.1)
CODE_20250618_003: Updated config.py with LAYER_NAME_MAP and list-based SQL patterns (v1.2)
🔍 What Worked
Replaced export_chart with generate_chart in main.py.
Created missing folders and .pptx templates.
Added case-insensitive layer matching and SQL logging.
Fixed SQL patterns to use LIKE '%pattern%' for partial matches.
Added LAYER_NAME_MAP to align logical names with ArcGIS layers.
Ensured charts render with proper labels, layout, and folder structure.
⚠️ Still Unresolved
Implement layer missing detection with console warnings.
Verify date calculator functions are correctly imported.
Add overwrite confirmation for existing charts.
Implement CSV export for bin counts.
Address chart title wrapping for long names.
Archive documentation as README_chart_export.md.
🔄 Next Steps
Develop unit tests for get_sql_pattern_for_crime.
Implement CSV export for chart data.
Automate PowerPoint embedding for charts.
Add layer missing detection warnings.
Schedule weekly report runs via Windows Task Scheduler.
Generate README_chart_export.md for archiving.
🧰 Tools/Tech Used
ArcPy, Python, matplotlib, logging, ArcGIS Pro
🧵 Key Decisions
Kept all scripts in 7_day_crime_report_tool_scripts folder.
Archived old .py files to avoid conflicts.
Used case-insensitive layer matching and LAYER_NAME_MAP for robustness.
Implemented list-based SQL patterns for partial calltype matches.
Documented checklist for tracking progress.
🔗 Related Conversations
None (no prior chats referenced).

---

### B. JSON Export

Below is the JSON export, which can be saved as `2025_06_18_16_41_00_SCRPA_Automation_Fixes.json`.

```json
{
  "metadata": {
    "title": "SCRPA Report Automation Debugging and Chart Export",
    "date": "2025-06-18",
    "participants": ["RAC", "ChatGPT"],
    "chat_name": "SCRPA Report Automation Fixes",
    "tags": ["ArcPy", "Python", "GIS", "Chart Export", "Error Handling", "Chart Formatting", "ArcPy Debugging", "Folder Management", "Logging", "SQL Patterns", "Layer Mapping", "Chart Automation"],
    "source": "Chat"
  },
  "summary": "This conversation resolved errors in an ArcGIS Pro Python script for crime report chart automation. Issues included ImportError, missing templates, layer mismatches, and SQL pattern errors. Fixes updated chart_export.py and config.py, added layer mapping, improved SQL patterns, and added logging. A checklist tracks completed and pending tasks.",
  "sections": [
    {
      "title": "Import Error: export_chart Not Found",
      "broken_code": {
        "id": "CODE_20250618_001_BROKEN",
        "language": "python",
        "content": "from chart_export import export_chart\nsuccess = export_chart(crime_type)"
      },
      "issue": "main.py tried to import export_chart, but chart_export.py only defined generate_chart.",
      "fixes": [
        "Add export_chart wrapper in chart_export.py.",
        "Update main.py to use generate_chart directly."
      ],
      "working_code": {
        "id": "CODE_20250618_001",
        "language": "python",
        "version": "v1.0",
        "content": "[Full chart_export.py content as provided previously]"
      }
    },
    {
      "title": "Missing PowerPoint Templates",
      "broken_code": {
        "id": "CODE_20250618_002_BROKEN",
        "language": "python",
        "content": "raise FileNotFoundError(f\"Missing required paths: {missing}\")"
      },
      "issue": "config.py expected a reports folder and three .pptx templates that didn’t exist.",
      "fixes": [
        "Create C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\_Hackensack_Data_Repository\\GIS_Tools\\SCRPA_Reports.",
        "Add blank SCRPA_7Day_Template.pptx, SCRPA_28Day_Template.pptx, SCRPA_YTD_Template.pptx in C:\\Templates\\."
      ],
      "working_code": null
    },
    {
      "title": "Missing 7-Day Incident Data",
      "broken_code": {
        "id": "CODE_20250618_003_BROKEN",
        "language": "python",
        "content": "lyr = next((l for l in map_obj.listLayers() if l.name == layer_name), None)"
      },
      "issue": "The 7-Day layer wasn’t found due to a naming mismatch.",
      "fixes": [
        "Use case-insensitive layer matching.",
        "Add logging for layer names and SQL queries."
      ],
      "working_code": {
        "id": "CODE_20250618_002",
        "language": "python",
        "version": "v1.1",
        "content": "lyr = next((l for l in map_obj.listLayers() if l.name.lower() == layer_name.lower()), None)\nlogging.info(f\"🔎 Looking for layer: {layer_name}\")\nlogging.info(f\"🗓️ {period} SQL: {sql}\")"
      }
    },
    {
      "title": "Missing Data Bars: Motor Vehicle Theft and Burglary Auto",
      "broken_code": {
        "id": "CODE_20250618_004_BROKEN",
        "language": "python",
        "content": "def get_sql_pattern_for_crime(crime_type):\n    patterns = {\n        \"Motor Vehicle Theft\": \"Motor Vehicle Theft\",\n        \"Burglary Auto\": \"Burglary - Auto\",\n        # ...\n    }\n    return patterns.get(crime_type)"
      },
      "issue": "Charts showed no data bars due to mismatched SQL patterns for calltype values like 'Motor Vehicle Theft - 2C:20-3'.",
      "fixes": [
        "Update get_sql_pattern_for_crime to return lists for partial matches.",
        "Add LAYER_NAME_MAP in config.py for layer name mapping.",
        "Modify chart_export.py to use LAYER_NAME_MAP."
      ],
      "working_code": {
        "id": "CODE_20250618_003",
        "language": "python",
        "version": "v1.2",
        "content": "[Full config.py content as provided above]"
      }
    }
  ],
  "checklist": {
    "accomplished": [
      "Charts render properly for all CRIME_TYPES.",
      "Correct layer mapping via LAYER_NAME_MAP.",
      "Multi-pattern SQL support for Burglary - Comm & Res.",
      "Bar labeling inside bars with black font and white background.",
      "X-axis orientation fixed (horizontal time bins).",
      "Chart layout with spacing, scaling, and tight layout.",
      "Automatic folder creation per crime type & report date.",
      "All charts exported without error via export_chart()."
    ],
    "pending": [
      {
        "issue": "Layer Missing Detection",
        "description": "Empty chart saved if layer doesn’t exist.",
        "fix": "Add print(f\"⚠️ No data layer for {crime_type} {period}\")."
      },
      {
        "issue": "Date Calculators",
        "description": "Assumed in memory, may fail if missing.",
        "fix": "Ensure config.py includes get_7day_period_dates, etc."
      },
      {
        "issue": "Folder Overwrite Confirmation",
        "description": "Existing charts silently overwritten.",
        "fix": "Add print(f\"🔄 Overwriting {out_path}\") or backup PNGs."
      },
      {
        "issue": "Optional CSV Export",
        "description": "No CSV with bin counts per period.",
        "fix": "Implement CSV export for counts per bin."
      },
      {
        "issue": "Chart Title Wrapping",
        "description": "Long crime types may overflow title.",
        "fix": "Use ax.set_title(..., wrap=True)."
      },
      {
        "issue": "Documentation Storage",
        "description": "Setup not archived in .md or .txt.",
        "fix": "Generate README_chart_export.md."
      }
    ],
    "enhancements": [
      "Add unit tests using mock arcpy objects.",
      "Add CLI script like python run_export.py --date 2025_06_17.",
      "Add support for weekly auto-run via Task Scheduler."
    ]
  },
  "session_summary_token": {
    "date": "2025-06-18",
    "context": "Debugged ArcGIS Pro script for crime report automation, fixing import errors, missing templates, layer mismatches, and SQL pattern errors.",
    "progress": "Updated chart_export.py with layer mapping and logging; fixed config.py for SQL partial matches; created required folders/templates; documented checklist.",
    "pending": "Implement CSV export, unit tests, PowerPoint embedding; address layer missing detection and title wrapping.",
    "tech": ["ArcPy", "Python", "matplotlib"],
    "ai": "ChatGPT",
    "chat_name": "SCRPA Report Automation Fixes"
  }
}
C. Updated Index File
Below is the updated INDEX.md file.
markdown
# Conversation Archive Index

| Date       | Chat Name                     | AI      | Key Topics                                      | Link                                      |
|------------|-------------------------------|---------|------------------------------------------------|-------------------------------------------|
| 2025-06-18 | SCRPA Report Automation Fixes | ChatGPT | ArcPy, Chart Export, Error Handling, Debugging, SQL Patterns, Layer Mapping, Chart Automation | [2025_06_18_16_41_00_SCRPA_Automation_Fixes.md](#) |

## Notes
- Links point to individual Markdown files in the archive.
- Key topics are derived from tags for quick reference.
Save as INDEX.md in 7_day_crime_report_tool_scripts\archive.
D. Version Control: Script Headers and Changelog
Script Headers:
All code snippets include version numbers (e.g., v1.0, v1.1, v1.2) and timestamps, as shown in the Markdown sections.
Example for config.py:
python
# config.py
# Author: R. A. Carucci
# Purpose: Centralized configuration for SCRPA report automation.
# Code ID: CODE_20250618_003
# Version: v1.2
# 🕒 2025-06-18 16:33:00
Changelog:
The changelog in the Markdown file tracks changes across versions.
Save as CHANGELOG.md in 7_day_crime_report_tool_scripts:
markdown
# Changelog for SCRPA Report Automation Scripts

## [1.2] - 2025-06-18
### Added
- `config.py`: Added `LAYER_NAME_MAP` for mapping logical crime types to ArcGIS layer names (CODE_20250618_003).
- `config.py`: Updated `get_sql_pattern_for_crime` to support list-based patterns for partial calltype matches.
### Changed
- `chart_export.py`: Updated layer name lookup to use `LAYER_NAME_MAP` (CODE_20250618_002).
- `chart_export.py`: Enhanced SQL logging for debugging missing data bars.

## [1.1] - 2025-06-18
### Changed
- `chart_export.py`: Added case-insensitive layer matching (CODE_20250618_002).
- `chart_export.py`: Improved y-axis padding for label visibility.
- `chart_export.py`: Added logging for SQL and layer names.

## [1.0] - 2025-06-18
### Added
- `chart_export.py`: Initial version with embedded data collection (CODE_20250618_001).
- `main.py`: Updated to use `generate_chart`.
- Created required folders and PowerPoint templates.
E. Insight Tagging
Expanded tags include:
Error Handling: Handling ImportError, FileNotFoundError, ModuleNotFoundError.
Chart Formatting: Adjusting y-axis padding, label placement, and styling.
ArcPy Debugging: Debugging layer mismatches and SQL queries.
Folder Management: Managing script duplicates and required paths.
Logging: Adding debug logs for SQL and layer visibility.
SQL Patterns: Implementing partial matches for calltype values.
Layer Mapping: Mapping logical crime types to ArcGIS layer names.
Chart Automation: Automating chart exports with folder creation and batch processing.
These tags are included in the Markdown metadata and session summary token.
F. Instructions for Saving
Markdown File: Save the Markdown content as 2025_06_18_16_41_00_SCRPA_Automation_Fixes.md in 7_day_crime_report_tool_scripts.
JSON File: Save the JSON content as 2025_06_18_16_41_00_SCRPA_Automation_Fixes.json in 7_day_crime_report_tool_scripts\archive.
Index File: Save INDEX.md in 7_day_crime_report_tool_scripts\archive.
Changelog: Save CHANGELOG.md in 7_day_crime_report_tool_scripts.
G. Next Steps
CSV Export: Implement CSV export for chart data bin counts.
Unit Tests: Develop tests for get_sql_pattern_for_crime.
PowerPoint Embedding: Automate chart embedding into PowerPoint templates.
Layer Missing Detection: Add console warnings for missing layers.
Title Wrapping: Use ax.set_title(..., wrap=True) for long names.
Documentation: Generate README_chart_export.md for archiving.
Scheduling: Set up Windows Task Scheduler for weekly runs.
Let me know if you want to implement the CSV export, generate README_chart_export.md, or proceed with any other pending tasks!