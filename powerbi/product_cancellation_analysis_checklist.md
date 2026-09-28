# Product & Cancellation Analysis build checklist

This is the sixth Power BI task: build and validate **only** the Product & Cancellation Analysis page.

Do not perform the final report-polish or screenshot task in this step.

## Page purpose

The page should answer four questions:

1. Which merchandise products generate the most net revenue?
2. Which merchandise products sell the most units?
3. How large is cancellation activity over time?
4. Which operational stock codes materially affect the financial totals?

Merchandise and operational stock codes must remain analytically separate.

## 1. Page setup

Create a report page named:

```text
Product & Cancellation Analysis
```

Use the same 16:9 page size, typography, spacing and title treatment as the first two report pages.

Recommended hierarchy:

1. title and slicers;
2. KPI strip;
3. two merchandise rankings;
4. cancellation trend;
5. merchandise detail and operational-entry tables.

## 2. Header and slicers

### Page title

Use:

```text
Product & Cancellation Analysis
```

Optional subtitle:

```text
Merchandise performance and operational adjustments
```

### Slicer 1 — Date

Field:

```text
dim_date[full_date]
```

Type:

```text
Between
```

### Slicer 2 — Country

Field:

```text
dim_country[country_name]
```

Default state: all countries.

### Slicer 3 — Product

Field:

```text
dim_product[product_description]
```

Enable search.

Do not add a hidden page-level merchandise filter. Merchandise filters belong only on merchandise-specific visuals so operational entries remain visible elsewhere on the page.

## 3. KPI strip

Use three cards:

1. Units Sold
2. Cancellation Invoices
3. Cancellation Value

### Unfiltered validation

| KPI | Expected value |
| --- | ---: |
| Units Sold | 11,672,569 |
| Cancellation Invoices | 8,292 |
| Cancellation Value | £1,526,667.86 |

These are whole-model measures. Do not filter the KPI strip to merchandise only.

## 4. Top merchandise products by net revenue

Visual:

```text
Horizontal bar chart
```

Title:

```text
Top Merchandise Products by Net Revenue
```

Category:

```text
dim_product[product_description]
```

Value:

```text
Net Revenue
```

Required visual-level filter:

```text
dim_product[product_type] = merchandise
```

Apply:

```text
Top N = 10 by Net Revenue
```

Sort descending by Net Revenue.

### Unfiltered validation

The first five rows should begin:

1. REGENCY CAKESTAND 3 TIER — £327,813.65
2. CREAM HANGING HEART T-LIGHT HOLDER — £253,720.02
3. JUMBO BAG RED RETROSPOT — £181,278.51
4. PARTY BUNTING — £147,948.50
5. ASSORTED COLOUR BIRD ORNAMENT — £131,413.85

Operational entries such as `DOTCOM POSTAGE`, `POSTAGE`, `AMAZON FEE` and `BANK CHARGES` must never appear in this chart.

## 5. Top merchandise products by units sold

Visual:

```text
Horizontal bar chart
```

Title:

```text
Top Merchandise Products by Units Sold
```

Category:

```text
dim_product[product_description]
```

Value:

```text
Units Sold
```

Required visual-level filter:

```text
dim_product[product_type] = merchandise
```

Apply:

```text
Top N = 10 by Units Sold
```

Sort descending by Units Sold.

Do not reuse the Net Revenue Top N filter. Revenue rank and unit-volume rank are intentionally different analytical views.

Validation requirement:

- every visible row must have `product_type = merchandise`;
- no operational code may enter the ranking;
- the visual must use the versioned `Units Sold` measure, not a raw implicit sum.

## 6. Cancellation trend

Visual:

```text
Line and clustered column chart
```

Title:

```text
Cancellation Activity by Month
```

Shared X-axis:

```text
dim_date[full_date]
```

Use month granularity on a continuous date axis.

Column Y-axis:

```text
Cancellation Invoices
```

Line Y-axis:

```text
Cancellation Value
```

Use the secondary Y-axis for Cancellation Value.

Label the axes clearly because the chart combines:

- invoice count;
- GBP value.

Do not imply that the two measures share the same unit.

### Source-period note

December 2011 is partial through **9 December 2011**.

Keep it visible in the time series but do not interpret its lower activity as a complete-month decline.

### Validation

With the full date range selected:

- total Cancellation Invoices = **8,292**;
- total Cancellation Value = **£1,526,667.86**.

The chart is descriptive. Do not label it as a return rate or matched-order cancellation rate.

## 7. Merchandise detail table

Visual:

```text
Table
```

Title:

```text
Merchandise Detail
```

Columns:

1. `dim_product[stock_code]`
2. `dim_product[product_description]`
3. Net Revenue
4. Units Sold
5. Sales Orders
6. Cancellation Value

Required visual-level filter:

```text
dim_product[product_type] = merchandise
```

Sort by Net Revenue descending by default.

Allow the Product slicer and chart selections to narrow this table.

Do not display surrogate product keys.

## 8. Operational entries

Visual:

```text
Table
```

Title:

```text
Operational Entries
```

Columns:

1. `dim_product[product_type]`
2. `dim_product[stock_code]`
3. `dim_product[product_description]`
4. Net Revenue
5. Cancellation Value

Required visual-level filter:

```text
dim_product[product_type] is not merchandise
AND
dim_product[product_type] is not unknown
```

Sort by absolute financial impact where practical; otherwise sort by Net Revenue and use the known validation rows below to confirm the table contents.

### Validation examples

The table must contain operational entries including:

| Type | Stock code | Description | Net Revenue |
| --- | --- | --- | ---: |
| shipping | DOT | DOTCOM POSTAGE | £322,647.47 |
| fee | AMAZONFEE | AMAZON FEE | -£260,763.58 |
| adjustment | B | Adjust bad debt | -£147,614.08 |
| shipping | POST | POSTAGE | £112,341.00 |
| adjustment | M | Manual | -£82,796.32 |

These entries remain part of overall financial measures even though they are excluded from merchandise rankings.

## 9. Layout

Recommended structure:

```text
┌──────────────────────────────────────────────────────────┐
│ Product & Cancellation Analysis   [Date] [Country] [Prod]│
├──────────────────────────────────────────────────────────┤
│ Units Sold │ Cancellation Invoices │ Cancellation Value │
├──────────────────────────────┬───────────────────────────┤
│ Top Merchandise by Revenue   │ Top Merchandise by Units │
├──────────────────────────────┴───────────────────────────┤
│              Cancellation Activity by Month             │
├──────────────────────────────┬───────────────────────────┤
│ Merchandise Detail           │ Operational Entries       │
└──────────────────────────────┴───────────────────────────┘
```

Keep the cancellation trend wide enough for the two axes to remain readable.

The two ranking charts should have equal dimensions so revenue and volume can be compared without giving one artificial visual priority.

## 10. Interaction checks

Confirm:

- Date slicer filters every visual.
- Country slicer filters every visual.
- Product slicer can narrow product-specific visuals and cancellation activity.
- Selecting a merchandise bar cross-filters the merchandise detail table.
- Selecting an operational entry does not cause it to appear in either merchandise ranking.
- Clearing all selections restores the three unfiltered KPI targets.
- No visual-level merchandise filter leaks into the KPI strip or operational table.

## 11. Final page validation

Before moving to final report review, confirm:

- Units Sold = **11,672,569** unfiltered;
- Cancellation Invoices = **8,292** unfiltered;
- Cancellation Value = **£1,526,667.86** unfiltered;
- REGENCY CAKESTAND 3 TIER leads the merchandise revenue ranking;
- operational entries never appear in merchandise rankings;
- DOTCOM POSTAGE appears in Operational Entries rather than product rankings;
- cancellation chart uses two clearly labelled axes;
- December 2011 is identified as a partial period;
- merchandise detail uses the documented `product_type` rule;
- no cancellation visual is described as a matched-order return probability.

## Stop point

Save the report after this page passes all checks.

Do not start final styling, screenshots or README completion yet. Those are separate tasks.
