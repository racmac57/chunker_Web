# Recreate Cad M Code Guide

**Processing Date:** 2025-10-27 19:47:17
**Source File:** Recreate_CAD_M_Code_Guide.docx
**Total Chunks:** 1

---

Guide to Recreating CAD M Code in Power Query
This guide provides all necessary steps, reminders, and tips to successfully recreate the CAD M code in Power Query for Excel. It is meant to help streamline the process whenever you receive a new CAD export. Step-by-Step Instructions
1. Open the CAD Excel export and convert the data into a table named 'Table1'. - Select the data. - Go to Insert > Table. - Name it 'Table1' under the Table Design tab. 2. Open the target Excel workbook (report file). 3. Open Power Query Editor:
   - Go to Data > Get Data > From Workbook if loading externally. - Or use Data > Get Data > From Table/Range if already within workbook. 4. In Power Query, open 'Advanced Editor'. 5. Paste the final M code provided for the report. 6. Update the 'ReportDate' in the code if a new report week is being calculated. 7. Load the supporting 7/28-Day CSV from this path:
   C:\Users\carucci_r\OneDrive - City of Hackensack\_Hackensack_Data_Repository\7Day_28Day_Cycle_CSV.csv
   - Ensure this file has the correct date structure and format. 8. Refresh the data model once complete. Additional Notes and Tips
• Always double-check column names in the CAD export. Key ones include:
  'FullAddress2', 'Time of Call', 'CADNotes', etc. • The M code assumes 'Time of Call' is a datetime column. Ensure this column is correctly formatted in Excel. • When editing address-based logic (e.g., 'Block' or 'Location'), ensure delimiters such as commas or ampersands are handled properly. • When replacing street types (e.g., 'Street' with 'St'), ensure multi-word names retain the first word (e.g., 'Lookout Avenue' becomes 'Lookout Ave', not just 'Ave'). • For intersections, logic uses text before the first comma and formats each road component. • Maintain consistency in the 7/28-Day CSV structure (headers and format). • Always back up previous versions of your code and source data before editing Power Query.

