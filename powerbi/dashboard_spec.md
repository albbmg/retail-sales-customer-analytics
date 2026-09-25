# Dashboard specification

The report is deliberately compact. Each page answers a distinct set of questions and avoids repeating visuals simply to fill space.

## 1. Executive Overview

### Purpose

Summarise the scale and evolution of the retail activity and make cancellation impact visible without allowing it to dominate the page.

### KPI cards

- Net Revenue
- Sales Orders
- Average Order Value
- Active Customers
- Cancellation Invoice Rate

### Visuals

1. **Monthly revenue trend**
   - Axis: `dim_date[full_date]` at month level
   - Values: Net Revenue, Non-Cancellation Revenue
   - Chart: line chart

2. **Revenue by country**
   - Category: `dim_country[country_name]`
   - Value: Net Revenue
   - Chart: horizontal bar chart
   - Show top countries; retain `Unknown` when present.

3. **Top products by net revenue**
   - Category: `dim_product[product_description]`
   - Value: Net Revenue
   - Chart: horizontal bar chart
   - Filter `dim_product[product_type] = "merchandise"`.

### Slicers

- Date range
- Country

## 2. Customer Analysis

### Purpose

Understand customer contribution, order activity and concentration among identified customers.

### KPI cards

- Active Customers
- Net Revenue per Active Customer
- Average Order Value

### Visuals

1. **Top customers**
   - Columns: customer ID, net revenue, sales orders, average order value
   - Sort: Net Revenue descending
   - Exclude the unknown customer member.

2. **Customer revenue vs. order frequency**
   - X: Sales Orders
   - Y: Net Revenue
   - Details: Customer ID
   - Chart: scatter plot

3. **Active customers over time**
   - Axis: month
   - Value: Active Customers
   - Chart: line chart

### Slicers

- Date range
- Country

## 3. Product & Cancellation Analysis

### Purpose

Compare product performance while keeping returns/cancellations visible as a separate operational signal.

### KPI cards

- Units Sold
- Cancellation Invoices
- Cancellation Value

### Visuals

1. **Top products by net revenue**
   - Category: product description
   - Value: Net Revenue
   - Filter `dim_product[product_type] = "merchandise"`.

2. **Top products by units sold**
   - Category: product description
   - Value: Units Sold
   - Filter `dim_product[product_type] = "merchandise"`.

3. **Cancellation trend**
   - Axis: month
   - Values: Cancellation Invoices, Cancellation Value
   - Prefer a combo chart only if the two scales remain readable; otherwise use separate aligned visuals.

4. **Product detail table**
   - Stock code
   - Product description
   - Net Revenue
   - Units Sold
   - Sales Orders
   - Cancellation Value
   - Filter `dim_product[product_type] = "merchandise"`.

5. **Operational entries**
   - Product type
   - Stock code
   - Product description
   - Net Revenue
   - Keep shipping, fees, adjustments, discounts, samples, vouchers and tests visible here rather than mixing them into merchandise rankings.

### Slicers

- Date range
- Country
- Product

## Interaction rules

- Dimension slicers filter all visuals on the page.
- Avoid bidirectional relationships or visual-specific calculations that change KPI definitions.
- Unknown members remain part of aggregate totals unless a ranking explicitly states that they are excluded.
- Cancellation Invoice Rate should be labelled exactly as defined; do not shorten it to “Cancellation Rate”, which could imply a matched-order cancellation probability that the source data cannot establish.
