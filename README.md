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

The source workbook is expected to contain:

- `Year 2009-2010`
- `Year 2010-2011`

Each sheet must expose the original columns in this order:

```text
Invoice
StockCode
Description
Quantity
InvoiceDate
Price
Customer ID
Country
```

Download and validate the source data:

```bash
python -m retail_analytics.extract
```

The workbook is stored at:

```text
data/raw/online_retail_II.xlsx
```

Use `--force` only when the source workbook needs to be downloaded again:

```bash
python -m retail_analytics.extract --force
```

### 2. Clean transformation layer

The two source periods are combined with Pandas and written to:

```text
data/processed/transactions.parquet
```

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

- source column names are normalised to a stable snake_case schema;
- dates and numeric fields are converted explicitly;
- missing customer IDs are preserved as nullable values;
- cancellations and negative adjustments are retained;
- duplicate source rows are not silently removed;
- `source_period` and `source_row` preserve row-level lineage;
- `is_cancellation` is derived from the invoice number;
- `line_amount` is calculated as `quantity * unit_price`.

Build the clean dataset:

```bash
python -m retail_analytics.transform
```

### 3. PostgreSQL staging

The Parquet dataset is loaded into:

```text
staging.transactions
```

The staging table mirrors the clean data contract and preserves the source lineage key.

The current loading strategy is a transactional full refresh:

1. create the staging schema and table if needed;
2. truncate the existing staging table;
3. bulk load the complete clean dataset with PostgreSQL `COPY`;
4. compare the loaded row count with the Parquet source;
5. commit only when both counts match.

If any step fails, the transaction is rolled back.

Load the clean data into PostgreSQL:

```bash
python -m retail_analytics.load
```

## Analytical model

The analytical layer is being built as a star schema with one fact table and four dimensions:

```text
              dim_date
                  │
                  │
dim_customer ─ fact_sales ─ dim_product
                  │
                  │
              dim_country
```

Planned tables:

- `analytics.fact_sales`
- `analytics.dim_date`
- `analytics.dim_customer`
- `analytics.dim_product`
- `analytics.dim_country`

The grain of `fact_sales` is **one product line within an invoice**.

Cancellations and negative adjustments remain part of the fact table so they can be analysed explicitly rather than removed during preparation.

## Measures

The initial analytical layer is designed around:

- Net revenue
- Orders
- Units sold
- Average order value
- Active customers
- Revenue per customer
- Cancellation rate

The final definitions will live alongside the SQL model and Power BI measures so each KPI has one documented business meaning.

## Running the project locally

### Python environment

The project uses Python 3.13.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Or on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

### PostgreSQL

Copy `.env.example` to a local `.env` file before changing the default database settings.

Start PostgreSQL:

```bash
docker compose up -d --wait postgres
```

Check its status:

```bash
docker compose ps
```

Stop the environment:

```bash
docker compose down
```

The database uses a Docker named volume. Use `docker compose down -v` only when an intentional database reset is required.

## Quality checks

Run the local checks with:

```bash
ruff check .
ruff format --check .
pytest
```

GitHub Actions runs the same checks on pull requests and on changes merged into `main`.

A separate integration job starts PostgreSQL with Docker and verifies the staging loader against a real database instance.

## Current progress

- [x] Define the analytical scope
- [x] Configure the Python project
- [x] Configure PostgreSQL with Docker
- [x] Add reproducible dataset acquisition and raw validation
- [x] Build the Pandas raw-to-clean transformation
- [x] Load clean transactions into PostgreSQL staging
- [ ] Build the analytical star schema
- [ ] Add SQL data-quality checks
- [ ] Develop sales, customer and product analysis
- [ ] Define final KPI calculations
- [ ] Build the Power BI dashboard
- [ ] Document findings and business conclusions
