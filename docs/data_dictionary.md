# Data dictionary

This document describes the persisted data contracts used by the project.

The raw UCI workbook remains unchanged. The first project-owned data contract is the clean Parquet layer, followed by PostgreSQL staging and the analytical star schema.

## Clean Parquet: `data/processed/transactions.parquet`

**Grain:** one source workbook row / transaction line.

| Column | Logical type | Nullable | Meaning |
| --- | --- | --- | --- |
| `invoice_no` | string | Yes | Source invoice number. Values beginning with `C` identify cancellation invoices. |
| `stock_code` | string | Yes | Source stock code. Can represent merchandise or an operational entry. |
| `description` | string | Yes | Source product or entry description. |
| `quantity` | integer | Yes | Signed source quantity. Negative values are retained. |
| `invoice_date` | datetime | No before staging | Source transaction timestamp. The staging loader rejects null dates. |
| `unit_price` | numeric | Yes | Source unit price in sterling. |
| `customer_id` | integer | Yes | Source customer identifier. Missing IDs are retained. |
| `country` | string | Yes | Source country label. |
| `source_period` | string | No | Original workbook sheet / period. |
| `source_row` | integer | No | Original Excel row number, including the header offset. |
| `is_cancellation` | boolean | No | True when `invoice_no` begins with `C`. |
| `line_amount` | numeric | Yes | `quantity * unit_price`; sign is preserved. |

The pair `(source_period, source_row)` is the row-level lineage key.

## PostgreSQL staging: `staging.transactions`

**Grain:** one clean transaction line.

Staging stays close to the clean Parquet contract and contains no dimensional business logic.

| Column | PostgreSQL type | Nullable | Notes |
| --- | --- | --- | --- |
| `invoice_no` | `TEXT` | Yes | Source invoice number. |
| `stock_code` | `TEXT` | Yes | Source stock code. |
| `description` | `TEXT` | Yes | Source description. |
| `quantity` | `INTEGER` | Yes | Signed quantity. |
| `invoice_date` | `TIMESTAMP` | No | Validated before load. |
| `unit_price` | `DOUBLE PRECISION` | Yes | Source price before analytical conversion to exact `NUMERIC`. |
| `customer_id` | `BIGINT` | Yes | Missing IDs remain null. |
| `country` | `TEXT` | Yes | Source country label. |
| `source_period` | `TEXT` | No | Lineage key component. |
| `source_row` | `INTEGER` | No | Lineage key component; must be >= 2. |
| `is_cancellation` | `BOOLEAN` | No | Cancellation flag from the clean layer. |
| `line_amount` | `DOUBLE PRECISION` | Yes | Signed clean-layer amount. |

**Primary key:** `(source_period, source_row)`.

## `analytics.dim_date`

**Grain:** one calendar date between the first and last transaction date.

| Column | Type | Meaning |
| --- | --- | --- |
| `date_key` | `INTEGER` | Deterministic `YYYYMMDD` key. |
| `full_date` | `DATE` | Calendar date, unique. |
| `year` | `SMALLINT` | Calendar year. |
| `quarter` | `SMALLINT` | Calendar quarter 1–4. |
| `month` | `SMALLINT` | Calendar month 1–12. |
| `month_name` | `TEXT` | Month label. |
| `day` | `SMALLINT` | Day of month. |
| `iso_day_of_week` | `SMALLINT` | ISO weekday 1–7. |
| `day_name` | `TEXT` | Weekday label. |
| `is_weekend` | `BOOLEAN` | True for ISO day 6 or 7. |

## `analytics.dim_customer`

**Grain:** one identified source customer, plus one explicit unknown member.

| Column | Type | Nullable | Meaning |
| --- | --- | --- | --- |
| `customer_key` | `BIGINT` | No | Deterministic surrogate key. Key `0` is Unknown customer. |
| `customer_id` | `BIGINT` | Yes | Original customer ID; null for the unknown member. |
| `customer_label` | `TEXT` | No | Stable display label. |

**Business key:** `customer_id`.

## `analytics.dim_product`

**Grain:** one source stock code, plus one explicit unknown member.

| Column | Type | Nullable | Meaning |
| --- | --- | --- | --- |
| `product_key` | `BIGINT` | No | Deterministic surrogate key. Key `0` is Unknown product. |
| `stock_code` | `TEXT` | Yes | Original stock code; null for the unknown member. |
| `product_description` | `TEXT` | No | Most recent non-null description observed for the stock code, or a fallback label. |
| `product_type` | `TEXT` | No | `merchandise`, `shipping`, `fee`, `adjustment`, `discount`, `sample`, `voucher`, `test` or `unknown`. |

**Business key:** `stock_code`.

Classification rules are documented in [`product_classification.md`](product_classification.md).

## `analytics.dim_country`

**Grain:** one distinct source country label, plus one explicit unknown member.

| Column | Type | Nullable | Meaning |
| --- | --- | --- | --- |
| `country_key` | `BIGINT` | No | Deterministic surrogate key. Key `0` is Unknown country. |
| `country_name` | `TEXT` | Yes | Original country label; null for the unknown member. |

**Business key:** `country_name`.

## `analytics.fact_sales`

**Grain:** one source transaction line.

| Column | Type | Nullable | Meaning |
| --- | --- | --- | --- |
| `source_period` | `TEXT` | No | Original workbook period. |
| `source_row` | `INTEGER` | No | Original workbook row. |
| `invoice_no` | `TEXT` | Yes | Source invoice number. |
| `invoice_timestamp` | `TIMESTAMP` | No | Transaction timestamp. |
| `date_key` | `INTEGER` | No | FK to `dim_date`. |
| `customer_key` | `BIGINT` | No | FK to `dim_customer`; key `0` for missing Customer ID. |
| `product_key` | `BIGINT` | No | FK to `dim_product`; key `0` for missing stock code. |
| `country_key` | `BIGINT` | No | FK to `dim_country`; key `0` for missing country. |
| `quantity` | `INTEGER` | Yes | Signed source quantity. |
| `unit_price` | `NUMERIC(18,4)` | Yes | Exact analytical unit price. |
| `line_amount` | `NUMERIC(20,4)` | Yes | Exact signed analytical line amount. |
| `is_cancellation` | `BOOLEAN` | No | Cancellation-invoice flag. |

**Primary key:** `(source_period, source_row)`.

The fact table preserves both merchandise and operational entries. Product rankings narrow the model through `dim_product.product_type`; they do not delete records from the fact table.

## Relationships

```text
dim_date      1 ─── * fact_sales
dim_customer  1 ─── * fact_sales
dim_product   1 ─── * fact_sales
dim_country   1 ─── * fact_sales
```

All analytical relationships are many-to-one from fact to dimension and use deterministic dimension keys.
