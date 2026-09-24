# KPI definitions

This document defines the business meaning of the core metrics used in the SQL analysis and, later, in Power BI.

The definitions are intentionally independent of the visual layer so the same metric means the same thing everywhere in the project.

## Net revenue

**Definition:** signed sum of `fact_sales.line_amount` across all transaction lines.

```text
Net revenue = Σ line_amount
```

Cancellations and negative adjustments are retained, so they reduce net revenue naturally.

## Non-cancellation revenue

**Definition:** signed sum of `line_amount` for rows whose invoice is not flagged as a cancellation.

This is used as the numerator for average order value. Non-cancellation negative adjustments remain part of the result rather than being hidden.

## Sales orders

**Definition:** distinct non-null invoice numbers where `is_cancellation = false`.

Cancellation invoices are not counted as sales orders.

## Units sold

**Definition:** sum of positive quantities on non-cancellation rows.

Negative adjustments are not treated as units sold.

## Average order value

**Definition:**

```text
Average order value =
    non-cancellation revenue / sales orders
```

The calculation is invoice-based and excludes cancellation invoices from both the revenue numerator and the order denominator.

## Active customers

**Definition:** distinct identified customers with at least one non-cancellation transaction in the selected period.

Rows mapped to the unknown-customer member are excluded from the customer count but remain in revenue totals.

## Net revenue per active customer

**Definition:** net revenue attributable to the active-customer population divided by the number of active customers.

Cancellations belonging to an active customer remain part of that customer's net revenue.

## Cancellation invoice rate

**Definition:**

```text
Cancellation invoice rate =
    distinct cancellation invoice numbers
    / distinct invoice numbers
```

This measures the share of invoice records that are flagged as cancellations.

It must **not** be interpreted as the probability that an original sales order was later cancelled. Cancellation invoices are represented as separate invoice records and the analytical model does not assume a one-to-one link back to an original invoice.

## Unknown members

Unknown customer, product and country members are preserved in the fact table rather than filtered out.

- Unknown customer rows contribute to overall revenue, but not to active-customer counts.
- Unknown products remain visible in total revenue but are excluded from the ranked product query.
- Unknown countries are reported explicitly as `Unknown`.

## Monetary precision

The analytical fact table stores `unit_price` and `line_amount` as PostgreSQL `NUMERIC` values. Reporting queries round display values to two decimal places while calculations use the stored exact values.
