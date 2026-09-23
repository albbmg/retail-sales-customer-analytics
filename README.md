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

The project will use the **Online Retail II** dataset from the UCI Machine Learning Repository.

It contains transactional data from a UK-based online retailer and includes invoices, products, quantities, prices, customers, countries and transaction dates.

Dataset source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

The raw dataset will not be committed to the repository. Instructions to download and prepare it will be added as part of the data pipeline.

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
```

The GitHub Actions workflow runs the same quality checks on pull requests and on changes merged into `main`. Pytest is enabled automatically once test files are added.

## Roadmap

- [x] Define project scope and V1 architecture
- [x] Set up the Python project structure
- [ ] Configure PostgreSQL with Docker
- [ ] Acquire and validate the raw dataset
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
