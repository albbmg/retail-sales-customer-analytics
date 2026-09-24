# Retail Sales & Customer Analytics

A reproducible analytical study of transactional retail data, focused on sales behaviour, customer activity, product performance, geographic distribution and order cancellations.

I started this project to explore how these parts of an online retail business interact over time using the **Online Retail II** dataset from the UCI Machine Learning Repository. The analysis is built as a complete data workflow, from the original workbook to a BI-ready analytical model.

## Questions explored

The study is organised around a small set of business questions:

- How do sales and order volumes evolve over time?
- Which customers contribute the most revenue and activity?
- Which products generate the highest revenue and unit volume?
- How is revenue distributed across countries?
- What is the financial impact of cancellations and negative adjustments?
- How do average order value and revenue per customer change over time?

The objective is to answer these questions from a reproducible data model rather than from one-off spreadsheet calculations.

## Architecture

```text
UCI Online Retail II
        ↓
Raw Excel workbook
        ↓
Validation
        ↓
Python / Pandas
        ↓
Clean Parquet
        ↓
PostgreSQL staging
        ↓
Analytical star schema
        ↓
Power BI
        ↓
Sales & customer analysis
```

The workflow deliberately separates raw data, clean data, staging and analytical layers so that transformations remain explicit and traceable.

## Dataset

The project uses **Online Retail II** from the UCI Machine Learning Repository.

It contains more than one million transactions from a UK-based online retailer between December 2009 and December 2011.

Dataset source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

Citation:

> Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

The dataset is distributed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license.

The raw workbook is not committed to Git. It is downloaded directly from UCI and validated before any transformation is applied.

## Data pipeline

### 1. Raw data acquisition and validation

The source workbook contains two periods, `Year 2009-2010` and `Year 2010-2011`, with the original UCI columns.

Download and validate the source data:

```bash
python -m retail_analytics.extract
```

The workbook is stored at `data/raw/online_retail_II.xlsx`.

### 2. Clean transformation layer

The two source periods are combined with Pandas and written to `data/processed/transactions.parquet`.

The clean schema is:

```text
invoice_no
stock_code
description
quantity
invoice_date
unit_price
customer_id
country
source_period
source_row
is_cancellation
line_amount
```

Important transformation decisions:

- source column names are normalised to snake_case;
- dates and numeric fields are converted explicitly;
- missing customer IDs are preserved;
- cancellations and negative adjustments are retained;
- duplicate source rows are not silently removed;
- `source_period` and `source_row` preserve row-level lineage;
- `line_amount` is calculated as `quantity * unit_price`.

Build the clean dataset:

```bash
python -m retail_analytics.transform
```

### 3. PostgreSQL staging

The Parquet dataset is loaded into `staging.transactions`.

The current loading strategy is a transactional full refresh using PostgreSQL `COPY`. The load is committed only when the database row count matches the Parquet source.

Load staging:

```bash
python -m retail_analytics.load
```

### 4. Analytical star schema

The staging layer is transformed into five analytical tables:

```text
              dim_date
                  │
                  │
dim_customer ─ fact_sales ─ dim_product
                  │
                  │
              dim_country
```

Tables:

- `analytics.fact_sales`
- `analytics.dim_date`
- `analytics.dim_customer`
- `analytics.dim_product`
- `analytics.dim_country`

The grain of `fact_sales` is **one product line within an invoice**.

Modelling decisions:

- surrogate dimension keys are generated deterministically so repeated rebuilds produce the same mappings;
- missing customer IDs map to an explicit `Unknown customer` member with key `0`;
- missing product and country values also map to key `0` rather than dropping the transaction;
- the product dimension uses the most recent non-null description observed for each `stock_code`;
- `dim_date` contains every calendar date between the first and last transaction;
- monetary measures are stored as exact PostgreSQL `NUMERIC` values;
- cancellations and negative adjustments remain in `fact_sales`;
- `source_period` and `source_row` remain the fact-table primary key and preserve lineage.

Rebuild the analytical model:

```bash
python -m retail_analytics.analytics
```

## Measures

The analytical layer is designed around:

- Net revenue
- Orders
- Units sold
- Average order value
- Active customers
- Revenue per customer
- Cancellation rate

The exact business definitions will be added alongside the analytical SQL used for the study.

## Running the project locally

The project uses Python 3.13.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
docker compose up -d --wait postgres
```

Run the pipeline in order:

```bash
python -m retail_analytics.extract
python -m retail_analytics.transform
python -m retail_analytics.load
python -m retail_analytics.analytics
```

Database connection settings are read from `.env` / environment variables. Real credentials are not committed.

## Quality checks

```bash
ruff check .
ruff format --check .
pytest
```

GitHub Actions also starts PostgreSQL in an isolated Docker environment and validates the database load and analytical model against a real database instance.

## Current progress

- [x] Define the analytical scope
- [x] Configure the Python project
- [x] Configure PostgreSQL with Docker
- [x] Add reproducible dataset acquisition and raw validation
- [x] Build the Pandas raw-to-clean transformation
- [x] Load clean transactions into PostgreSQL staging
- [x] Build the analytical star schema
- [ ] Add SQL data-quality checks
- [ ] Develop sales, customer and product analysis
- [ ] Define final KPI calculations
- [ ] Build the Power BI dashboard
- [ ] Document findings and business conclusions
