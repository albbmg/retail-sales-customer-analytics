# Power BI relationship checklist

This is the second Power BI setup step: create and validate the semantic-model relationships after the five analytical tables have been imported.

Do not add DAX measures in this step.

## Relationships to create

Create exactly these four active relationships:

| Dimension | Fact | Cardinality | Cross-filter direction |
| --- | --- | --- | --- |
| `dim_date[date_key]` | `fact_sales[date_key]` | One-to-many (1:*) | Single |
| `dim_customer[customer_key]` | `fact_sales[customer_key]` | One-to-many (1:*) | Single |
| `dim_product[product_key]` | `fact_sales[product_key]` | One-to-many (1:*) | Single |
| `dim_country[country_key]` | `fact_sales[country_key]` | One-to-many (1:*) | Single |

The filter direction must propagate from each dimension table to `fact_sales`.

## How to configure each relationship

In **Model view**:

1. Open **Manage relationships** or drag the dimension key onto the matching fact-table key.
2. Confirm the dimension table is on the **1** side.
3. Confirm `fact_sales` is on the ***` side.
4. Set **Cross-filter direction** to **Single**.
5. Keep **Make this relationship active** enabled.
6. Save the relationship.

Repeat the same process for all four dimensions.

## What the final model should look like

```text
              dim_date
                  1
                  │
                  *
dim_customer 1 ─ * fact_sales * ─ 1 dim_product
                  *
                  │
                  1
              dim_country
```

There should be no direct relationships between dimension tables.

There should be no many-to-many relationships.

There should be no bidirectional relationships.

## Validation

Before moving on to DAX, confirm all of the following:

- four relationship lines are visible;
- every relationship is active;
- every dimension is on the **1** side;
- `fact_sales` is on the **many** side;
- every relationship uses **Single** cross-filter direction;
- filters propagate from dimension to fact;
- there are no relationship warnings or ambiguous paths;
- there is no relationship involving `staging.transactions`.

A correctly configured model should contain one central fact table surrounded by the four dimensions.

## Why this model is deliberate

The PostgreSQL layer already guarantees uniqueness of the dimension surrogate keys and referential integrity from `fact_sales`.

Using one-to-many, single-direction relationships preserves the star-schema design in Power BI and avoids unnecessary bidirectional filter paths.

Microsoft Power BI relationship documentation:

https://learn.microsoft.com/power-bi/transform-model/desktop-relationships-understand

Microsoft star-schema guidance:

https://learn.microsoft.com/power-bi/guidance/star-schema
