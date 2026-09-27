# Customer Analysis build checklist

This is the fifth Power BI task: build and validate **only** the Customer Analysis page.

Do not build the Product & Cancellation Analysis page in this step.

## Page purpose

The page should show:

1. how many identified customers are active;
2. how much revenue is associated with the active-customer population;
3. which identified customers contribute the most revenue;
4. how customer revenue relates to order frequency;
5. how the active-customer count evolves over time.

The source contains a material number of transactions without Customer ID. Customer-level rankings and scatter plots must therefore exclude the explicit Unknown customer member rather than assigning those transactions to known customers.

## 1. Page setup

Create a report page named:

```text
Customer Analysis
```

Use the same page size, typography, spacing and visual conventions as Executive Overview.

Recommended hierarchy:

1. title and slicers;
2. customer KPI strip;
3. top-customer table and customer scatter plot;
4. active-customer trend.

## 2. Header and slicers

### Page title

Use:

```text
Customer Analysis
```

Optional subtitle:

```text
Identified customer activity and revenue contribution
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

Do not add a customer slicer to this page. A list of thousands of customer IDs adds noise without helping the main analysis.

## 3. Customer KPI strip

Use three cards:

1. Active Customers
2. Net Revenue per Active Customer
3. Average Order Value

### Unfiltered validation

| KPI | Expected value |
| --- | ---: |
| Active Customers | 5,881 |
| Net Revenue per Active Customer | £2,841.24 |
| Average Order Value | £459.10 |

### Important metric boundary

`Active Customers` and `Net Revenue per Active Customer` explicitly exclude the Unknown customer according to their documented definitions.

`Average Order Value` remains the whole-business order measure. Do not silently redefine it on this page with a hidden customer filter.

If a known customer is selected interactively, the standard filter context can narrow the measure normally.

## 4. Top identified customers

Visual:

```text
Table
```

Title:

```text
Top Customers by Net Revenue
```

Columns:

1. `dim_customer[customer_id]`
2. Net Revenue
3. Sales Orders
4. Average Order Value

Required visual-level filter:

```text
dim_customer[customer_id] is not blank
```

Apply:

```text
Top N = 15 by Net Revenue
```

Sort by Net Revenue descending.

Do not use `customer_label` when the numeric Customer ID is enough; the repeated word "Customer" adds no information in a compact table.

### Unfiltered validation

The first five rows should begin:

| Customer ID | Net Revenue | Sales Orders | Average Order Value |
| --- | ---: | ---: | ---: |
| 18102 | £598,215.22 | 145 | £4,198.77 |
| 14646 | £523,342.07 | 152 | £3,477.65 |
| 14156 | £296,564.69 | 156 | £2,012.48 |
| 14911 | £270,248.53 | 398 | £743.65 |
| 17450 | £233,579.39 | 51 | £4,842.61 |

The table is a ranking of **identified customers only**.

## 5. Customer revenue vs. order frequency

Visual:

```text
Scatter chart
```

Title:

```text
Customer Revenue vs. Order Frequency
```

Configure:

- X-axis: Sales Orders
- Y-axis: Net Revenue
- Details: `dim_customer[customer_id]`

Tooltips:

- Average Order Value
- Units Sold
- Cancellation Invoices

Required visual-level filter:

```text
dim_customer[customer_id] is not blank
```

Do not use bubble size initially. Two analytical axes are enough; adding a third encoded magnitude would make an already dense chart harder to read.

### Validation

Customer **14911** should sit noticeably farther right than the other leading customers because it has **398 sales orders**, while customers such as **18102** and **14646** are higher on revenue with substantially fewer orders.

That contrast is useful: high revenue contribution and high order frequency are related dimensions, not interchangeable rankings.

Do not add a trend line or causal interpretation.

## 6. Active customers over time

Visual:

```text
Line chart
```

Title:

```text
Active Customers by Month
```

X-axis:

```text
dim_date[full_date]
```

Use month granularity on a continuous date axis.

Y-axis:

```text
Active Customers
```

Sort chronologically ascending.

### Validation

Two high-activity complete months should include:

- November 2011 — **1,665** active customers
- November 2010 — **1,607** active customers

As on Executive Overview, December 2011 is partial through 9 December. Do not interpret its lower count as a complete-month decline.

## 7. Missing Customer ID note

Add a small informational note, not a KPI card:

```text
22.77% of transaction lines have no Customer ID.
Customer-level visuals exclude these unknown customers.
```

This limitation is analytically important because those rows represent **13.68% of total net revenue**.

Keep the note visually secondary to the actual customer metrics.

Do not remove Unknown customer transactions from the underlying model or from whole-business totals.

## 8. Layout

Recommended structure:

```text
┌──────────────────────────────────────────────────────────┐
│ Customer Analysis                   [Date]      [Country]│
├──────────────────────────────────────────────────────────┤
│ Active Customers │ Revenue / Customer │ Average Order   │
├──────────────────────────────┬───────────────────────────┤
│ Top Customers by Net Revenue │ Revenue vs. Order Freq.  │
│                              │                           │
├──────────────────────────────┴───────────────────────────┤
│                Active Customers by Month                │
└──────────────────────────────────────────────────────────┘
│ small data-coverage note                                │
```

The top-customer table should be wide enough that customer IDs and monetary values remain readable without horizontal scrolling.

The scatter plot should receive enough width for outliers to remain distinguishable.

## 9. Interaction checks

Confirm:

- Date slicer filters all visuals.
- Country slicer filters all visuals.
- Selecting a customer row cross-filters the scatter and trend.
- Selecting a scatter point cross-filters the table and trend.
- Clearing selections restores the unfiltered KPI values.
- Unknown customer never appears in the table or scatter.
- Unknown customer transactions remain part of whole-business measures according to the documented KPI definitions.

## 10. Final page validation

Before moving to Product & Cancellation Analysis, confirm:

- Active Customers = **5,881** unfiltered;
- Net Revenue per Active Customer = **£2,841.24** unfiltered;
- Average Order Value = **£459.10** unfiltered;
- Customer 18102 ranks first by Net Revenue;
- Customer 14911 has the highest Sales Orders count among the displayed top-five revenue customers;
- the scatter excludes blank Customer ID;
- November 2011 shows 1,665 active customers;
- the missing-customer limitation is visible but not presented as a KPI;
- no customer-level visual makes claims about the unidentified-customer population.

## Stop point

Save the report after this page passes the checks.

Do not build the Product & Cancellation Analysis page yet.
