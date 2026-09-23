# Retail Sales & Customer Analytics

End-to-end Data Analytics / Business Intelligence portfolio project focused on retail sales and customer behaviour.

The goal is to build a small but complete analytics workflow, starting from raw transactional data and ending with a business-focused Power BI dashboard.

## Project objective

This project is intended to demonstrate practical skills in:

- Python and Pandas for data cleaning and transformation
- SQL for data modelling and analytical queries
- PostgreSQL as the analytical database
- Power BI for KPI reporting and visual analysis
- Docker for a reproducible local environment
- Git and GitHub for version control and project documentation

The project will be developed incrementally. The priority is to keep the solution understandable, reproducible and easy to explain in a technical interview.

## Dataset

The project uses **Online Retail II** from the UCI Machine Learning Repository.

It contains more than one million transactions from a UK-based online retailer between December 2009 and December 2011.

Dataset source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

Citation:

> Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

The dataset is distributed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license.

The raw workbook is intentionally excluded from Git. The project downloads it directly from UCI and validates its structure before any cleaning or transformation takes place.

### Raw data contract

The source workbook is expected to contain these two sheets:

- `Year 2009-2010`
- `Year 2010-2011`

Each sheet must expose the original source columns in this order:

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

Download and validate the dataset:

```bash
python -m retail_analytics.extract
```

The command stores the workbook at `data/raw/online_retail_II.xlsx`, verifies the expected sheets and columns, and reports the row count for each sheet.

Use `--force` only when the raw workbook needs to be downloaded again:

```bash
python -m retail_analytics.extract --force
```

## V1 scope

The first version will follow this flow:

```text
Raw dataset
    ↓
Python / Pandas
    ↓
PostgreSQL
    ↓
SQL analytical model
    ↓
Power BI
    ↓
Business insights
```

The initial analysis will focus on:

- Sales evolution over time
- Number of orders and average order value
- Customer activity and top customers
- Product performance
- Geographic sales distribution
- Order cancellations and their impact

## Planned data model

The analytical layer will use a simple star schema:

- `fact_sales`
- `dim_date`
- `dim_customer`
- `dim_product`
- `dim_country`

The grain of `fact_sales` will be one product line within an invoice.

## Initial KPIs

The first dashboard version is expected to include:

- Net revenue
- Orders
- Units sold
- Average order value
- Active customers
- Revenue per customer
- Cancellation rate

Definitions will be documented alongside the SQL and Power BI implementation so the calculations remain consistent across the project.

## Local development

The project uses Python 3.13 and a standard `src/` package layout.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and development tools:

```bash
python -m pip install -e ".[dev]"
```

Run the local quality checks:

```bash
ruff check .
ruff format --check .
pytest
```

The GitHub Actions workflow runs the same quality checks on pull requests and on changes merged into `main`.

### PostgreSQL

Create a local `.env` file from `.env.example` before changing the default database credentials.

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Check its status:

```bash
docker compose ps
```

Stop the environment:

```bash
docker compose down
```

The database is stored in a Docker named volume, so stopping the container does not remove local data. Use `docker compose down -v` only when an intentional database reset is required.

## Roadmap

- [x] Define project scope and V1 architecture
- [x] Set up the Python project structure
- [x] Configure PostgreSQL with Docker
- [x] Add reproducible raw dataset acquisition and validation
- [ ] Build the Pandas cleaning pipeline
- [ ] Create the analytical data model
- [ ] Add SQL data-quality checks
- [ ] Develop sales, customer and product analysis
- [ ] Define KPIs and Power BI measures
- [ ] Build the Power BI dashboard
- [ ] Document business insights and final architecture

## Project status

**In progress.**

The repository is intentionally being built in small, reviewable steps. Documentation will evolve together with the implementation rather than describing features that do not exist yet.
