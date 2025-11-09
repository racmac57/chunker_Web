# Chunk 4 Summary

both and provide the updated version using the data attached
# Load the uploaded Excel file to examine sheet names and sample data
file_path = "/mnt/data/Policy_Training_Monthly.xlsx"
excel_file = pd.ExcelFile(file_path)
# Display available sheets and preview the first few rows of each
sheet_data_preview = {sheet: excel_file.parse(sheet).head() for sheet in excel_file.sheet_names}
sheet_data_preview
 26 Unnamed: 27  \
 0          9  ...          23          24          25          26          27   
 1        NaN  ...         NaN         NaN         NaN         NaN         NaN   
 2         20  ...         NaN         NaN         NaN         NaN         NaN   
 3        NaN  ...         NaN         NaN         NaN         NaN         NaN   
 4        160  ...         NaN         NaN         NaN         NaN         NaN   
   Unnamed: 28 Unnamed: 29 Unnamed: 30 Unnamed: 31 Unnamed: 32  
 0          28          29          30          31       Total  
 1         NaN         NaN         NaN         NaN         NaN  
 2         NaN         NaN         NaN         NaN         NaN  
 3         NaN         NaN         NaN         NaN         NaN  
 4         NaN         NaN         NaN         NaN         NaN  
 [5 rows x 33 columns],
 'FOR MONTHLY':                Tracked Items  06-23  07-23  08-23  09-23  10-23  11-23   \
 0      Handgun Qual Attendees     38      0     34      0      3      3   
 1  Handgun Training Attendees      4      0      0      0     68      0   
 2        Rifle Qual Attendees      5      3      0      1      0      0   
 3    Rifle Training Attendees      0      0      0      0      3      3   
 4      Sub-Gun Qual Attendees      0      5      0      7      0      0   
   12-23  Unnamed: 8 Unnamed: 9 Unnamed: 10 Unnamed: 11 Unnamed: 12 Unnamed: 13  
 0     41        NaN        NaN         NaN         NaN         NaN         NaN  
 1      0        NaN        NaN         NaN         NaN         NaN         NaN  
 2     16        NaN        NaN         NaN         NaN         NaN         NaN  
 3      0        NaN        NaN         NaN         NaN         NaN         NaN  
 4      5        NaN        NaN         NaN         NaN         NaN         NaN  ,
 '2023':   Basic Operator Weapons Training    1    2    3    4    5    6    7    8   9  \
 0                Handgun Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN NaN   
 1                  Rifle Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN NaN   
 2                Sub-Gun Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN NaN   
 3          Taser (Basic Operator)  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN NaN   
 4                             NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN NaN   
    ...  23  24  25  26  27  28  29  30  31  Total  
 0  ... NaN NaN NaN NaN NaN NaN NaN NaN NaN    NaN  
 1  ... NaN NaN NaN NaN NaN NaN NaN NaN NaN    NaN  
 2  ... NaN NaN NaN NaN NaN NaN NaN NaN NaN    NaN  
 3  ... NaN NaN NaN NaN NaN NaN NaN NaN NaN    NaN  
 4  ... NaN NaN NaN NaN NaN NaN NaN NaN NaN    NaN  
 'Sheet3':    Unnamed: 0           Unnamed: 1       Unnamed: 2              Unnamed: 3  \
 0         NaN                  NaN              NaN                     NaN   
 1         NaN           Start Date  Course Duration             Course Name   
 2         NaN  2024-09-03 00:00:00                4  Methods of Instruction   
 3         NaN  2024-09-03 00:00:00                3           Colt Armorer    
 4         NaN  2024-09-06 00:00:00                4   RDF Operator Training   
        Unnamed: 4    Unnamed: 5  Unnamed: 6  Unnamed: 7 Unnamed: 8 Unnamed: 9  \
 0             NaN           NaN         NaN         NaN        NaN        NaN   
 1  # \nAttendees   Total \nCost         NaN         NaN      45538      45541   
 2               1           250         NaN         NaN      45538      45540   
 3               1           250         NaN         NaN      45541      45546   
 4               1             0         NaN         NaN      45541      45541   
    ... Unnamed: 13 Unnamed: 14 Unnamed: 15          Unnamed: 16  \
 0  ...         NaN         NaN         NaN                  NaN   
 1  ...         250         250         NaN           Start Date   
 2  ...         250         250         NaN  2024-09-03 00:00:00   
 3  ...           0           0         NaN  2024-09-06 00:00:00   
 4  ...           0           0         NaN  2024-09-23 00:00:00   
        Unnamed: 17                Unnamed: 18     Unnamed: 19  Unnamed: 20  \
 0              NaN                        NaN             NaN          NaN   
 1  Course Duration      Firearms Course Name   # \nAttendees   Total\nCost   
 2                3      Colt Armorer Training               3            0   
 3                1        Pistol Marksmanship               1            0   
 4                9  Recruit Fireams Training                2            0   
   Unnamed: 21 Unnamed: 22  
 0         NaN         NaN  
 1         NaN         NaN  
 2         NaN         NaN  
 3         NaN         NaN  
 4         NaN         NaN  
 [5 rows x 23 columns],
 '25_Jan':   Basic Operator Weapons Training   01   02   03   04   05   06   07   08  \
 0                Handgun Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
 1                  Rifle Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
 2                Sub-Gun Training  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
 3          Taser (Basic Operator)  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN   
 4     Instructor Weapons Training  1.0  2.0  3.0  4.0  5.0  6.0  7.0  8.0   
     09  ... Unnamed: 33  BWC Review(s) for the Month  Unnamed: 35  \
 0  NaN  ...          NaN                          NaN          NaN   
 1  NaN  ...          NaN                          NaN          NaN   
 2  NaN  ...          NaN                          NaN          NaN   
 3  NaN  ...          NaN                          NaN          NaN   
 4  9.0  ...          NaN                          NaN          NaN   
    Start Date   End Date  Course Duration  \
 0  2025-01-02 2025-01-27              1.0   
 1  2025-01-14 2025-01-14              1.0   
 2  2025-01-15 2025-01-15              1.0   
 3  2025-01-21 2025-01-25              1.0   
 4  2025-01-21 2025-01-24              1.0   
    Course Name of InPerson | Non-Firearms Related  # Attendees   \
 0                                   CPR Training           32.0   
 1                              Case Law for Cops            1.0   
 2            Concealed Carry and FARS Background            1.0   
 3                              Driving Simulator            1.0   
 4                               Defensive Tactics           1.0   
    Cost Per Member  Total Cost  
 0             10.0         0.0  
 1            195.0         0.0  
 2              0.0         0.0  
 3              0.0         0.0  
 4              0.0         0.0  
 [5 rows x 43 columns],
 '25_Feb':   Basic Operator Weapons Training   01   02   03   04   05   06   07   08  \
     09  ...    25    26    27    28  Column1  Column2  Column3  Total  \
 0  NaN  ...   NaN   NaN   NaN   NaN      NaN      NaN      NaN      0   
 1  NaN  ...   NaN   NaN   NaN   NaN      NaN      NaN      NaN      0   
 2  NaN  ...   NaN   NaN   NaN   NaN      NaN      NaN      NaN      0   
 3  NaN  ...   NaN   NaN   NaN   NaN      NaN      NaN      NaN      0   
 4  9.0  ...  25.0  26.0  27.0  28.0  Column1  Column2  Column3  Total   
    Unnamed: 33  BWC Review(s) for the Month  
 0          NaN                          NaN  
 1          NaN                          NaN  
 2          NaN                          NaN  
 3          NaN                          NaN  
 4          NaN                          NaN  
 [5 rows x 35 columns],
 '25_Mar':   Basic Operator Weapons Training   01   02   03   04   05   06   07   08  \
 '25_Apr':   Basic Operator Weapons Training   01   02   03   04   05   06   07   08  \
     09  ...    22    23    24    25    26    27    28    29    30  Total  
 0  NaN  ...   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN      0  
 1  NaN  ...   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN      0  
 2  NaN  ...   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN      0  
 3  NaN  ...   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN      0  
 4  9.0  ...  22.0  23.0  24.0  25.0  26.0  27.0  28.0  29.0  30.0  Total  
 [5 rows x 32 columns],
 'April':   Basic Operator Weapons Training   01   02   03   04   05   06   07   08  \
 '25_May':                  Tracked Items  01  02  03  04  05  06  07  08  09  ...  \
 0             Handgun Training NaN NaN NaN NaN NaN NaN NaN NaN NaN  ...   
 1               Rifle Training NaN NaN NaN NaN NaN NaN NaN NaN NaN  ...   
 2             Sub-Gun Training NaN NaN NaN NaN NaN NaN NaN NaN NaN  ...   
 3       Taser (Basic Operator) NaN NaN NaN NaN NaN NaN NaN NaN NaN  ...   
 4  Handgun Instructor Training NaN NaN NaN NaN NaN NaN NaN NaN NaN  ...
