# Executive Overview build checklist

This is the fourth Power BI task: build and validate **only** the Executive Overview page.

Do not build the Customer Analysis or Product & Cancellation Analysis pages in this step.

## Page purpose

The page should answer three questions quickly:

1. What is the overall scale of the retail activity?
2. How does revenue evolve over time?
3. Which countries and merchandise products contribute most revenue?

Cancellation impact remains visible through the KPI strip and the gap between net and non-cancellation revenue, but it should not dominate the page.

## 1. Page setup

Create a new report page named:

```text
Executive Overview
```

Recommended page format:

```text
16:9
```

Use a restrained layout with clear spacing and one visual hierarchy:

1. page title and slicers;
2. KPI strip;
3. monthly revenue trend;
4. country and merchandise rankings.

Avoid decorative shapes, gauges, pie charts, gradients or duplicated metrics.

## 2. Header and slicers

### Page title

Use:

```text
Retail Sales Overview
```

Optional subtitle:

```text
Online Retail II · Dec 2009 – Dec 2011
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

Default state: full available date range.

### Slicer 2 — Country

Field:

```text
dim_country[country_name]
```

Default state: all countries.

Keep both slicers in the header area so they are easy to identify without competing with the analytical visuals.

## 3. KPI strip

Use the current **Card** visual and place these five versioned measures in one horizontal KPI strip:

1. Net Revenue
2. Sales Orders
3. Average Order Value
4. Active Customers
5. Cancellation Invoice Rate

Do not use implicit column aggregations.

### Unfiltered validation

With no slicer selection, the cards must display:

| KPI | Expected value |
| --- | ---: |
| Net Revenue | £19,287,250.57 |
| Sales Orders | 45,336 |
| Average Order Value | £459.10 |
| Active Customers | 5,881 |
| Cancellation Invoice Rate | 15.46% |

Use compact display units only when they remain unambiguous. The tooltip or underlying measure must retain the exact value.

## 4. Monthly revenue trend

Visual:

```text
Line chart
```

Title:

```text
Monthly Revenue Trend
```

X-axis:

```text
dim_date[full_date]
```

Use month granularity and a continuous date axis.

Y-axis measures:

- Net Revenue
- Non-Cancellation Revenue

Sort chronologically ascending.

Do not add a separate legend field; the two measures themselves identify the series.

### Important source note

December 2011 contains source data only through **9 December 2011**.

Keep the month visible so the full source period remains transparent, but add a short note near the visual:

```text
December 2011 is partial through 9 Dec.
```

Do not interpret the December 2011 drop as a complete-month performance decline.

### Visual validation

The highest-revenue complete month should be:

```text
November 2011 — £1,461,756.25 net revenue
```

November 2010 should also appear among the strongest months:

```text
£1,422,654.64 net revenue
```

## 5. Revenue by country

Visual:

```text
Horizontal bar chart
```

Title:

```text
Net Revenue by Country
```

Y-axis / category:

```text
dim_country[country_name]
```

X-axis / value:

```text
Net Revenue
```

Sort by Net Revenue descending.

Apply a visual-level **Top N = 8** filter by Net Revenue to keep the page readable.

Do not remove the explicit Unknown country member globally. If it enters the selected Top N under a filtered view, it should remain visible.

### Unfiltered validation

The leading bar must be:

```text
United Kingdom — £16,382,583.90
```

The next four highest-revenue countries should be:

1. EIRE
2. Netherlands
3. Germany
4. France

## 6. Top merchandise products

Visual:

```text
Horizontal bar chart
```

Title:

```text
Top Merchandise Products by Net Revenue
```

Y-axis / category:

```text
dim_product[product_description]
```

X-axis / value:

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

Do **not** recreate the merchandise rule with text patterns or stock-code prefixes.

### Unfiltered validation

The first five products should be:

1. REGENCY CAKESTAND 3 TIER — £327,813.65
2. CREAM HANGING HEART T-LIGHT HOLDER — £253,720.02
3. JUMBO BAG RED RETROSPOT — £181,278.51
4. PARTY BUNTING — £147,948.50
5. ASSORTED COLOUR BIRD ORNAMENT — £131,413.85

Operational entries such as `DOTCOM POSTAGE`, `POSTAGE`, `AMAZON FEE` and `BANK CHARGES` must not appear in this visual.

## 7. Layout

Recommended structure:

```text
┌──────────────────────────────────────────────────────────┐
│ Retail Sales Overview             [Date]      [Country] │
├──────────────────────────────────────────────────────────┤
│ Net Rev │ Orders │ AOV │ Customers │ Cancellation Rate │
├──────────────────────────────────────────────────────────┤
│                                                        │
│               Monthly Revenue Trend                    │
│                                                        │
├───────────────────────────┬──────────────────────────────┤
│ Net Revenue by Country    │ Top Merchandise Products    │
│                           │ by Net Revenue               │
└───────────────────────────┴──────────────────────────────┘
```

The monthly trend should receive the most visual space because time evolution is the primary analytical view on this page.

The two ranking charts should have equal visual weight.

## 8. Interaction checks

Confirm:

- Date slicer filters every visual on the page.
- Country slicer filters every visual on the page.
- Selecting a country bar updates the KPI strip, monthly trend and product ranking.
- Selecting a product bar can cross-filter the other visuals without changing any KPI definition.
- Clearing selections restores the exact unfiltered KPI targets.
- No visual uses a hidden alternative measure or implicit aggregation.

## 9. Final page validation

Before moving to the Customer Analysis page, confirm:

- five KPI values match the validated totals;
- the monthly chart uses both revenue measures;
- December 2011 is clearly labelled as partial;
- United Kingdom is the leading country;
- product ranking contains merchandise only;
- no operational stock code appears in the product chart;
- slicers and visual selections update the page consistently;
- titles use business language rather than database column names;
- there are no unnecessary legends, gridlines or decorative elements competing with the data.

## Stop point

Save the Power BI report/project after the page passes these checks.

Do not build the second page yet.
