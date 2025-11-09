# Chunk 9 Summary

import numpy as np
# Create new Start Date and End Date columns based on Month column in historical data
def infer_dates(month_str):
        dt = datetime.strptime(month_str + "-01", "%m-%y-%d")
        start_date = dt
        end_date = dt.replace(day=28)  # Just use 28th as placeholder to ensure month boundary
        return start_date, end_date
    except:
        return np.nan, np.nan
# Apply function to infer dates
dates = historical_df["Month"].apply(lambda m: infer_dates(str(m).strip()))
historical_df["Start Date"] = [d[0] for d in dates]
historical_df["End Date"] = [d[1] for d in dates]
historical_df["Start Time"] = ""
historical_df["End Time"] = ""
# Reorder and rename columns to match clean format
final_columns_order = [
    "Start Date", "Start Time", "End Date", "End Time", "Course Name",
    "Training Type", "Sub-Type", "Course Duration", "# Attendees",
    "Cost Per Person", "Total Cost", "Instructor (Y/N)", "Month"
# Map reformatted data
clean_df = pd.DataFrame({
    "Start Date": historical_df["Start Date"],
    "Start Time": historical_df["Start Time"],
    "End Date": historical_df["End Date"],
    "End Time": historical_df["End Time"],
    "Course Name": historical_df["Course Name"],
    "Training Type": historical_df["Training Type"],
    "Sub-Type": historical_df["Sub-Type"],
    "Course Duration": historical_df["Course Duration"],
    "# Attendees": historical_df["# Attendees"],
    "Cost Per Person": historical_df["Cost Per Person"],
    "Total Cost": historical_df["Total Cost"],
    "Instructor (Y/N)": historical_df["Instructor (Y/N)"],
    "Month": historical_df["Month"]
# Save to a clean, flat Excel file without formatting, validation or protection
clean_file_path = "/mnt/data/Clean_Historical_Training_Data.xlsx"
clean_df.to_excel(clean_file_path, index=False)
'/mnt/data/Clean_Historical_Training_Data.xlsx'
Here is a clean, flat version of the historical training data that avoids corruption and includes:
Inferred Start Date and End Date from the Month field
Blank placeholders for Start Time and End Time
No sheet protection or validation that could trigger Excel errors
📥 Download the clean historical training file
Would you like me to help you import this clean dataset into your current master workbook? the start and end times are missing is that beause the data is not entered in the historical data? Yes, exactly — the Start Time and End Time are missing because the original historical summary data (from the "Yearly Totals" sheet) only provided:
Monthly totals per training type (e.g., 10 Rifle Trainings in 07-23)
No specific dates or times for when those sessions occurred
Since there's no session-level granularity (like “Rifle Training on 07/15/23 at 10:00 AM”), it's not possible to accurately reconstruct Start Time or End Time.
