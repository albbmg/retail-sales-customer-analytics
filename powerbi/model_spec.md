# Semantic model specification

## Storage mode

All five PostgreSQL analytical tables use **Import** mode.

## Relationships

| From | To | Cardinality | Cross-filter |
| --- | --- | --- | --- |
| `dim_date[date_key]` | `fact_sales[date_key]` | 1:* | Single |
| `dim_customer[customer_key]` | `fact_sales[customer_key]` | 1:* | Single |
| `dim_product[product_key]` | `fact_sales[product_key]` | 1:* | Single |
| `dim_country[country_key]` | `fact_sales[country_key]` | 1:* | Single |

All relationships are active and filter from dimension to fact.

No bidirectional relationships are required.

## Date table

Mark `dim_date` as the date table using:

```text
dim_date[full_date]
```

Disable automatic date/time for the report so the explicit date dimension remains the single calendar model.

Recommended sort configuration:

- `month_name` sorted by `month`
- `day_name` sorted by `iso_day_of_week`

## Field visibility

Hide technical relationship and lineage fields from normal report authoring:

### fact_sales

- `source_period`
- `source_row`
- `date_key`
- `customer_key`
- `product_key`
- `country_key`

### dimensions

Hide the surrogate-key columns:

- `dim_date[date_key]`
- `dim_customer[customer_key]`
- `dim_product[product_key]`
- `dim_country[country_key]`

The fields remain in the model and can still be inspected when troubleshooting relationships.

## Data categories

Set:

```text
dim_country[country_name] → Country/Region
```

## Currency

The UCI source describes `UnitPrice` as sterling (£), so monetary measures use GBP formatting.

This formatting is presentational only. The underlying PostgreSQL values remain exact `NUMERIC` values.

## Measure location

Measures are attached to `fact_sales` and grouped with display folders:

- `KPIs`
- `Cancellations`

Their business definitions live in `docs/kpi_definitions.md`.
