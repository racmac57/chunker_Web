# Power BI Layout JSON Prompt Guide

**Exported:** 10/27/2025 11:13:53  
**Link:** [https://gemini.google.com/u/1/app/148eadbef19fdec9](https://gemini.google.com/u/1/app/148eadbef19fdec9)

## Prompt:
Can you help me writing a prompt for obtaining Jason code for a Power BI custom layout?

## Response:
Certainly! To write an effective prompt for obtaining JSON code for a Power BI custom layout, you'll want to be as specific as possible about your desired layout. Here's a structured approach with examples you can adapt:

**Core Elements of the Prompt:**

1.  **Clear Objective:** State explicitly what you want.
2.  **Target Output:** Specify "JSON code" for a "Power BI custom layout."
3.  **Key Layout Properties:** Detail the most important aspects of your layout.
4.  **Specific Visuals:** List the visuals you want and their properties.
5.  **Page/Canvas Size (Optional but Recommended):** Define the overall dimensions.
6.  **Thematic/Styling (Optional but Recommended):** Mention any aesthetic preferences.
7.  **Constraints/Exclusions (Optional):** If there's anything you specifically _don't_ want.
8.  **Example/Reference (Optional but helpful):** If you have a mental image, describe it or refer to common patterns.

* * *

**Prompt Template with Examples:**

"I need JSON code to define a custom layout for a Power BI report page.

**The layout should include the following visuals and properties:**

*   **Page Name:** \[e.g., "Sales Overview," "Executive Dashboard"\]
*   **Page Size:** \[e.g., "16:9 ratio," "Custom (1920x1080 pixels)"\]
*   **Visual 1: \[Visual Type\]**
    *   **Position:** \[e.g., "Top Left," "Coordinates (x: 10, y: 10)"\]
    *   **Size:** \[e.g., "Width: 400, Height: 250," "Occupies 1/3 of the page width"\]
    *   **Title:** \[e.g., "Total Sales by Month," "Revenue Trend"\]
    *   **Specific Properties (if applicable):** \[e.g., "Enable drillthrough," "No background," "Border color: #RRGGBB"\]
*   **Visual 2: \[Visual Type\]**
    *   **Position:** \[e.g., "Below Visual 1," "Coordinates (x: 10, y: 270)"\]
    *   **Size:** \[e.g., "Width: 400, Height: 200"\]
    *   **Title:** \[e.g., "Sales by Product Category"\]
    *   **Specific Properties:** \[e.g., "Show data labels," "Legend position: Bottom"\]
*   **Visual 3: \[Visual Type\]**
    *   **Position:** \[e.g., "Right of Visual 1 and 2, spanning their height," "Coordinates (x: 420, y: 10)"\]
    *   **Size:** \[e.g., "Width: 800, Height: 480"\]
    *   **Title:** \[e.g., "Regional Sales Map"\]
    *   **Specific Properties:** \[e.g., "Zoom enabled," "Tooltip content: Sales Amount, Profit"\]
*   **\[Add more visuals as needed, following the same structure\]**

**General Layout Considerations:**

*   **Responsiveness (Optional):** \[e.g., "Should be somewhat responsive to different screen sizes," "Fixed layout is fine."\]
*   **Spacing:** \[e.g., "Maintain a consistent 20-pixel padding between visuals."\]
*   **Background:** \[e.g., "Transparent page background," "Solid white background."\]
*   **Visual Order:** \[e.g., "Ensure Visual 1 is on top of Visual 2 if they overlap."\]

**Exclude/Avoid:**

*   \[e.g., "Do not include any slicers," "No unnecessary borders around visuals."\]

**Example Layout Concept (if helpful):** \[Describe a high-level concept, e.g., "Think of a dashboard with a top row for KPIs, a middle section for trend charts, and a bottom section for detailed tables."\]

The output should be valid JSON that can be pasted directly into a Power BI Desktop `layout.json` file for a custom theme."

* * *

**Example of a Specific Prompt:**

"I need JSON code to define a custom layout for a Power BI report page named 'Executive Summary'.

The page size should be a 16:9 ratio.

The layout should include the following visuals and properties:

*   **Visual 1: Card Visual**
    *   **Position:** Top Left (x: 50, y: 50)
    *   **Size:** Width: 200, Height: 100
    *   **Title:** "Total Revenue"
    *   **Specific Properties:** White background, no border.
*   **Visual 2: Line Chart**
    *   **Position:** Right of Visual 1 (x: 270, y: 50)
    *   **Size:** Width: 700, Height: 300
    *   **Title:** "Revenue Trend by Month"
    *   **Specific Properties:** X-axis shows months, Y-axis shows revenue, data labels enabled.
*   **Visual 3: Table Visual**
    *   **Position:** Below Visual 1, spanning the remaining width (x: 50, y: 170)
    *   **Size:** Width: 920, Height: 400
    *   **Title:** "Top 10 Products by Sales"
    *   **Specific Properties:** Scroll enabled, striped rows.
*   **Visual 4: Donut Chart**
    *   **Position:** Below Line Chart (x: 270, y: 370)
    *   **Size:** Width: 350, Height: 200
    *   **Title:** "Sales by Region"
    *   **Specific Properties:** Show percentages in slices, legend on the right.

**General Layout Considerations:** Maintain a 20-pixel padding between visuals where possible. The page background should be transparent.

The output should be valid JSON that can be pasted directly into a Power BI Desktop `layout.json` file for a custom theme."

* * *

By using this structured approach, you'll provide enough detail for an AI to generate accurate and usable JSON for your Power BI custom layout. Remember that the more specific you are, the better the result will be.

## Prompt:
What is the term in Power BI where you go to the custom setting for the actual formats of the pages?

## Response:
The term in Power BI where you go to the custom settings for the actual formats of the pages is typically referred to as **Canvas settings** or **Page settings** within the **Format pane**.

When you have **no visual selected** on your Power BI report page, the "Format pane" (the paint roller icon in the Visualizations pane) will display options related to the entire page. Within this, you'll find sections like:

*   **Canvas settings:** This is where you adjust the page size (e.g., 16:9, 4:3, Letter, or **Custom** with specific pixel dimensions) and alignment.
*   **Canvas background:** For setting the background color or image of the page.
*   **Wallpaper:** For the background _behind_ the report canvas itself.

While you interact with these settings in the Power BI Desktop UI, the underlying mechanism for custom themes and layouts, especially when you're looking for JSON code, is often related to **Power BI Themes**. These themes are essentially JSON files that define default formatting for pages, visuals, text, and colors, allowing for a standardized and custom look across reports. The "layout" section within a comprehensive Power BI theme JSON file can specify the initial size and position of elements on a page.



---
Powered by [Gemini Exporter](https://www.geminiexporter.com)