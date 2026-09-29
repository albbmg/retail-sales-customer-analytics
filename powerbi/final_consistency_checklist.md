# Power BI final consistency review

This is the seventh Power BI task: review the three completed report pages for visual, interaction and accessibility consistency.

Do not add new analytical measures or new report pages in this step.

## Scope

Review these pages together:

1. Executive Overview
2. Customer Analysis
3. Product & Cancellation Analysis

The purpose is to make the report feel like one coherent analytical product rather than three independently formatted pages.

## 1. Page structure

Confirm all three pages use:

- 16:9 page size;
- the same outer page margins;
- the same title position;
- the same slicer height and alignment;
- the same KPI-card height;
- consistent spacing between sections;
- consistent visual-title placement.

Avoid one-off visual sizes unless a specific chart genuinely needs more space.

## 2. Titles and terminology

Use the same business-language naming everywhere.

Preferred terms:

- Net Revenue
- Sales Orders
- Average Order Value
- Active Customers
- Cancellation Invoice Rate
- Cancellation Value
- Units Sold
- Merchandise
- Operational Entries

Do not switch between synonyms such as:

- Revenue / Sales / Turnover for the same metric;
- Orders / Invoices when the metric specifically means Sales Orders;
- Cancellation Rate when the measure is Cancellation Invoice Rate.

Do not expose database-style labels such as:

- customer_key
- product_key
- date_key
- line_amount

in report titles or visible field labels.

## 3. Slicer consistency

Date slicer:

```text
dim_date[full_date]
```

Use the same **Between** style on every page where Date is present.

Country slicer:

```text
dim_country[country_name]
```

Use the same style, width and position across all pages.

Product slicer exists only on Product & Cancellation Analysis.

Confirm slicer fonts, headers, borders and backgrounds are identical across pages.

## 4. KPI card consistency

Cards must share:

- the same font family;
- the same title size;
- the same callout-value size;
- the same border treatment;
- the same corner radius;
- the same internal padding;
- the same background treatment;
- the same number-format conventions.

Formatting:

- GBP values: two decimals where space allows;
- percentages: two decimals;
- counts: whole numbers with thousands separators;
- negative monetary values: visibly negative.

Do not use different compact-unit rules on different pages for the same measure.

## 5. Color system

Use a restrained report-wide palette.

Recommended semantic roles:

- primary analytical series;
- secondary comparison series;
- neutral supporting elements;
- cancellation / negative financial values;
- selection/highlight state.

Do not assign a unique decorative color to every visual.

Do not use color as the only way to communicate a difference between series.

Avoid red/green-only comparisons.

Maintain sufficient contrast between text and background.

## 6. Chart formatting

Across all charts:

- keep titles aligned consistently;
- remove unnecessary visual borders;
- remove unnecessary gridlines;
- keep axis-label font sizes consistent;
- use the same monetary display style;
- use descending sort for ranked bar charts;
- use chronological ascending sort for time-series charts;
- avoid redundant legends where measure names already identify series.

Do not add data labels everywhere by default. Use them only where they improve reading rather than duplicating axis information.

## 7. Time-series consistency

All monthly time-series visuals must:

- use `dim_date[full_date]`;
- use month granularity;
- sort chronologically;
- retain December 2011;
- make the partial-period limitation visible.

Use the same wording wherever the note appears:

```text
December 2011 is partial through 9 Dec.
```

Do not show different versions of the warning on different pages.

## 8. Merchandise consistency

Every merchandise ranking or merchandise detail visual must use:

```text
dim_product[product_type] = merchandise
```

Do not rebuild the rule with:

- stock-code prefixes;
- text matching;
- numeric-only checks;
- visual-specific manual exclusions.

Operational entries must remain visible only in the dedicated operational analysis.

## 9. Visual interactions

Use **Edit interactions** to review every selectable visual.

Confirm:

- slicers filter the intended visuals;
- bar selections cross-filter or cross-highlight only where useful;
- a chart selection does not produce a misleading KPI interpretation;
- clearing a selection reliably restores the page;
- no visual unexpectedly disables another page-level analytical view.

If a cross-highlight is difficult to interpret, prefer cross-filtering.

Keep interaction behaviour consistent for similar visual types across pages.

## 10. Accessibility review

For every meaningful visual:

- add concise alt text;
- set a logical tab order;
- remove purely decorative objects from tab order;
- use descriptive titles;
- avoid unnecessary acronyms;
- confirm text/background contrast is sufficient;
- do not rely on color alone to communicate meaning.

Recommended tab order on each page:

1. page title;
2. slicers;
3. KPI cards;
4. primary chart;
5. secondary charts;
6. detail tables;
7. explanatory note.

Check that keyboard navigation follows the visual reading order.

## 11. Visual-specific alt text

Alt text should describe the visual's analytical role rather than repeat its title.

Examples:

### Executive Overview monthly trend

```text
Monthly net and non-cancellation revenue across the available retail period.
```

### Customer scatter

```text
Identified customers positioned by sales-order frequency and net revenue.
```

### Cancellation trend

```text
Monthly cancellation invoice count and cancellation value shown on separate scales.
```

Do not hard-code changing metric values into static alt text.

## 12. Page navigation

Keep the three page names short and stable:

1. Executive Overview
2. Customer Analysis
3. Product & Cancellation Analysis

Do not add duplicate navigation buttons unless the final report format genuinely benefits from them.

If navigation buttons are added later, they must use the same order on every page.

## 13. Cross-page metric checks

Before final sign-off, confirm that the same measure returns the same unfiltered value wherever it appears.

Key controls:

| Measure | Expected unfiltered value |
| --- | ---: |
| Net Revenue | £19,287,250.57 |
| Sales Orders | 45,336 |
| Average Order Value | £459.10 |
| Active Customers | 5,881 |
| Units Sold | 11,672,569 |
| Cancellation Invoices | 8,292 |
| Cancellation Invoice Rate | 15.46% |
| Cancellation Value | £1,526,667.86 |

If the same measure differs between pages with all slicers cleared, inspect page-level and visual-level filters before changing the DAX.

## 14. Final consistency pass

Review the report at normal viewing size and confirm:

- no page looks visually denser than the others without analytical reason;
- no title is truncated;
- no table requires horizontal scrolling at the intended report size;
- no slicer overlaps another object;
- no KPI card changes width unexpectedly;
- no visual displays raw database field names;
- all report notes use the same typography;
- December 2011 is consistently marked as partial;
- Unknown customer and operational-code limitations remain visible where analytically relevant.

## Stop point

After this review passes, save the report/project.

Do not create screenshots or update the root README to claim the Power BI report is complete yet.

Final screenshots and repository completion are the next separate task.
