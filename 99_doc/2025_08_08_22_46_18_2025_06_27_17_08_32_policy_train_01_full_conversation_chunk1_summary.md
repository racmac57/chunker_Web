# Chunk 1 Summary

Skip to content
Chat history

You said:
Policy Training Monthly
Unable to display visualization
review the attached file for errors, also provide ways to better set up the tables example table _25_03. also make sue the totals for the table on each sheet match up with the _mom_policy_training to the corresponding month
ChatGPT said:
Analyzed
Always show details
import pandas as pd
# Load the Excel file and list sheet names
excel_path = "/mnt/data/Policy_Training_Monthly.xlsx"
xlsx = pd.ExcelFile(excel_path)
sheet_names = xlsx.sheet_names
sheet_names
Result
['January',
 'February',
 'March',
 'May',
 'June',
 'July',
 'August',
 'September',
 'October',
 'November',
 'December',
 'Table74',
 'Table75',
 'Sheet2',
 'Sheet1',
 'AllTraining',
 'Old Monthly',
 'FOR MONTHLY',
 '2023',
 'Sheet3',
 '25_Jan',
 '25_Feb',
 '25_Mar',
 '25_Apr',
 'April',
 '25_May',
 'InPerson OnLine Firearms',
 'Yearly Totals',
 'pt',
 'Sheet4',
 'InPerson OnLine Firearms (2)']
# Load relevant sheets to compare totals and extract tables like _25_03 (assumed to be '25_Mar' for March)
# Also load '_mom_policy_training' data, which could be monthly sheets like 'March', 'April', etc. # Define mapping of '25_' sheets to corresponding month sheets
month_sheet_mapping = {
    '25_Jan': 'January',
    '25_Feb': 'February',
    '25_Mar': 'March',
    '25_Apr': 'April',
    '25_May': 'May'
}
# Load the sheets for analysis
tables_25 = {key: xlsx.parse(key) for key in month_sheet_mapping.keys()}
mom_policy_training = {value: xlsx.parse(value) for value in month_sheet_mapping.values()}
# Display sample of data from one table to understand structure
tables_25['25_Mar'].head()
STDOUT/STDERR
/home/sandbox/.local/lib/python3.11/site-packages/openpyxl/worksheet/_reader.py:312: UserWarning: Web Extension extension is not supported and will be removed
  warn(msg)
  Basic Operator Weapons Training   01   02   03   04   05   06   07   08  \
0                Handgun Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
1                  Rifle Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
2                Sub-Gun Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
3          Taser (Basic Operator)  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
4     Instructor Weapons Training  1.0  2.0  3.0  4.0  5.0  6.0  7.0  8.0   
    09  ...
