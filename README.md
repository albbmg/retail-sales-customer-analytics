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
- `product_type` separates merchandise from shipping, fees, adjustments, discounts, samples, vouchers and test records using rules derived from the full-dataset profile;
- `dim_date` contains every calendar date between the first and last transaction;
- monetary measures are stored as exact PostgreSQL `NUMERIC` values;
- cancellations and negative adjustments remain in `fact_sales`;
- `source_period` and `source_row` remain the fact-table primary key and preserve lineage.

Rebuild the analytical model:

```bash
python -m retail_analytics.analytics
python -m retail_analytics.quality
```

## Analytical data quality

The analytical model is checked against staging with a versioned SQL suite after each rebuild.

The checks cover:

- staging and fact-table row counts;
- one-to-one source lineage;
- fact-to-dimension relationships;
- unknown customer, product and country mappings;
- cancellation flags;
- date keys;
- unit prices and line amounts;
- uniqueness of dimension business keys.

Run the checks with:

```bash
python -m retail_analytics.quality
```

Each rule returns a check name and the number of violating rows. Any non-zero result fails the command.

## Scope and limitations

The analysis is intentionally limited to what can be supported by the transaction data:

- the dataset represents one historical retail context, so findings are interpreted within that period rather than as current market behaviour;
- revenue is derived from transaction quantity and unit price; the source does not provide product cost or margin information, so the study does not infer profitability;
- transactions without a customer identifier are retained and mapped to the explicit unknown-customer member;
- cancellations and negative adjustments remain visible instead of being discarded or silently netted out;
- product descriptions can vary over time, so the product dimension uses a documented canonicalisation rule while the fact table retains source-level lineage.

These constraints are treated as part of the analytical model rather than as data to hide during preparation.

## SQL analysis and KPI definitions

The business definitions used by the analysis are documented in [`docs/kpi_definitions.md`](docs/kpi_definitions.md).

Versioned SQL queries live under `sql/analysis/` and cover:

- overall KPIs;
- monthly sales trends;
- customer performance;
- merchandise product performance;
- operational stock-code impact;
- country performance;
- cancellation trends.

The queries run against the analytical star schema rather than staging, keeping business analysis separate from ingestion and preparation.

Product-classification rules are documented in [`docs/product_classification.md`](docs/product_classification.md).

The validated analytical observations are summarised in [`docs/findings.md`](docs/findings.md). Every reported figure is linked back to versioned SQL in the repository.

## Documentation

The main technical and analytical decisions are documented separately so the README can stay focused on the end-to-end workflow:

- [Data dictionary](docs/data_dictionary.md)
- [KPI definitions](docs/kpi_definitions.md)
- [Product classification](docs/product_classification.md)
- [Validated findings](docs/findings.md)
- [Power BI semantic model and report specification](powerbi/README.md)

## Running the project locally

The project is tested on Python 3.13; the supported runtime range is declared in `pyproject.toml`.

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
python -m retail_analytics.quality
```

Database connection settings are read from `.env` / environment variables. Real credentials are not committed.

## Quality checks

```bash
ruff check .
ruff format --check .
pytest -m "not integration"
```

PostgreSQL integration tests are isolated with the `integration` marker and run separately in CI against a disposable database instance.

GitHub Actions also starts PostgreSQL in an isolated Docker environment and validates the database load and analytical model against a real database instance.

## Full dataset validation

A separate manual GitHub Actions workflow runs the complete pipeline against the official UCI source rather than a small fixture.

It downloads the workbook, builds the clean layer, loads PostgreSQL, rebuilds the star schema, runs all analytical quality checks and prints a reproducible Markdown profile of the resulting dataset.

The validation workflow is intentionally manual because it processes the complete 1M+ row source dataset and is used for release-level verification rather than for every pull request.

The same validation outputs can be generated locally after the analytical model has been built:

```bash
python -m retail_analytics.profile
python -m retail_analytics.study_summary
```

The profile focuses on source characteristics and data-quality context. The study summary uses versioned analytical SQL to produce comparable-period, concentration, geographic, customer-coverage and product-type metrics.

## Power BI

The semantic-model relationships, DAX/TMDL measures and three-page dashboard specification are versioned under [`powerbi/`](powerbi/).

The report consumes the PostgreSQL `analytics` schema in Import mode so the visual layer does not redefine preparation or business rules.

## License

Project code and documentation are released under the [MIT License](LICENSE).

The **Online Retail II** source dataset is a separate work published by the UCI Machine Learning Repository under **CC BY 4.0**. The dataset is downloaded from UCI at runtime and is not redistributed by this repository.

## Current progress

- [x] Define the analytical scope
- [x] Configure the Python project
- [x] Configure PostgreSQL with Docker
- [x] Add reproducible dataset acquisition and raw validation
- [x] Build the Pandas raw-to-clean transformation
- [x] Load clean transactions into PostgreSQL staging
- [x] Build the analytical star schema
- [x] Add SQL data-quality checks
- [x] Develop sales, customer and product analysis
- [x] Define final KPI calculations
- [ ] Build and validate the Power BI report
- [x] Document validated analytical findings
