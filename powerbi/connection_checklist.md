# Power BI connection checklist

This is the first Power BI setup step for the project: connect Power BI Desktop to the local PostgreSQL analytical model and load the five star-schema tables.

No relationships or DAX measures are configured in this step.

## 1. Make sure PostgreSQL is ready

Start the local database:

```bash
docker compose up -d --wait postgres
```

The analytical model must already exist in PostgreSQL. If the database has been reset, rebuild the pipeline before opening Power BI:

```bash
python -m retail_analytics.extract
python -m retail_analytics.transform
python -m retail_analytics.load
python -m retail_analytics.analytics
python -m retail_analytics.quality
```

## 2. Open the PostgreSQL connector

In Power BI Desktop:

1. Select **Get data**.
2. Choose **PostgreSQL database**.
3. Use the local PostgreSQL connection values from your `.env` file.
4. Select **Import** as the data connectivity mode.

For the default local development configuration:

```text
Server: localhost:5432
Database: retail_analytics
```

Authenticate with **Database** credentials using the PostgreSQL username and password configured in the local `.env` file.

Do not store real credentials in this repository.

Power BI Desktop includes the PostgreSQL provider required by the connector in current supported versions, so no separate Npgsql installation should normally be necessary.

## 3. Load only the analytical tables

In the Navigator, select exactly these tables from the `analytics` schema:

- `analytics.fact_sales`
- `analytics.dim_date`
- `analytics.dim_customer`
- `analytics.dim_product`
- `analytics.dim_country`

Do not load `staging.transactions` into the Power BI model. Staging is an ingestion layer, not part of the semantic model.

Choose **Load** after confirming the five tables.

## 4. Connection validation

Before creating relationships or measures, confirm:

- five tables are present in the model;
- `fact_sales` is the only fact table;
- all four dimensions are present;
- `dim_product` contains `product_type`;
- `dim_date` contains `full_date`;
- `fact_sales` contains `line_amount`, `quantity` and `is_cancellation`;
- no `staging` table has been imported.

At this point, stop. Relationship creation is the next separate setup task.

## Reference

Microsoft Power Query PostgreSQL connector documentation:

https://learn.microsoft.com/power-query/connectors/postgresql
