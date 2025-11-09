# Power BI Matrix Visual Setup Guide
// 2025-06-13-15-45-00
// ASSIGNMENT_MASTER/matrix_visual_guide
// Author: R. A. Carucci
// Purpose: Step-by-step guide to create arrest data matrix visual matching pivot table format

## Step 1: Create DAX Measures

Create these measures in your data model:

### Female Count
```dax
F = CALCULATE(
    COUNTROWS('ASSIGNMENT_MASTER'),
    'ASSIGNMENT_MASTER'[sex] = "F"
)
```

### Male Count
```dax
M = CALCULATE(
    COUNTROWS('ASSIGNMENT_MASTER'),
    'ASSIGNMENT_MASTER'[sex] = "M"
)
```

### Total Count
```dax
Total = CALCULATE(
    COUNTROWS('ASSIGNMENT_MASTER')
)
```

## Step 2: Configure Matrix Visual

### Add Matrix Visual to Report
1. Insert → Visualizations → Matrix

### Configure Fields
- **Rows**: 
  - Drag `state_county_residence` to Rows
  - Drag `city_residence` to Rows (below state/county)
- **Values**: 
  - Drag `F` measure to Values
  - Drag `M` measure to Values  
  - Drag `Total` measure to Values

### Format the Matrix

#### Row Headers
- Turn ON "Stepped layout"
- Turn ON "Expand all down one level in the hierarchy"

#### Column Headers
- Set to show: F, M, Total

#### Grand Totals
- Turn ON "Row grand totals"
- Turn ON "Column grand totals"

#### Conditional Formatting (Yellow Grand Total Row)
1. Select the matrix
2. Format → Conditional formatting → Background color
3. Rules based on: Values
4. Apply to: Totals only
5. Color: Yellow (#FFFF00)

## Step 3: Apply Rolling 12-Month Filter

### Option A: Page-Level Filter
1. Filters pane → Add filter → `arrest_date`
2. Filter type: Relative date
3. Show items when value: is in the last 12 months

### Option B: Date Table Approach
If you want more control, create a Date table with this column:
```dax
IsInRolling12 = 
IF(
    'Date'[Date] >= EDATE(TODAY(), -12) + 1 &&
    'Date'[Date] <= EOMONTH(TODAY(), -1),
    1, 0
)
```

Then filter where `IsInRolling12 = 1`

## Step 4: Final Styling

### Match Your Image Format
- **Font**: Calibri or similar
- **Borders**: Thin black lines
- **Alternating row colors**: Light gray/white
- **Grand total row**: Yellow background
- **Text alignment**: Center for numbers, left for text

### Remove Unnecessary Elements
- Turn OFF column subtotals (you only want grand totals)
- Turn OFF "Show on rows" for subtotals if they appear

## Expected Result
Your matrix should show:
- State/County hierarchy in rows
- Cities nested under each state/county
- F, M, Total columns
- Yellow grand total row at bottom
- Proper count aggregations matching your sample data