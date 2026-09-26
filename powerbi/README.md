# Power BI

The Power BI layer consumes the PostgreSQL `analytics` star schema and does not introduce a second set of business rules.

## Connection

Follow the first-step checklist in [`connection_checklist.md`](connection_checklist.md).

Use the native **PostgreSQL database** connector in Power BI Desktop.

Recommended connectivity mode: **Import**.

The source is a bounded historical dataset and the analytical tables are rebuilt explicitly in PostgreSQL, so importing the model keeps report interaction fast without adding a DirectQuery dependency that the study does not need.

Import only:

- `analytics.fact_sales`
- `analytics.dim_date`
- `analytics.dim_customer`
- `analytics.dim_product`
- `analytics.dim_country`

Database credentials stay in the local Power BI connection and are never stored in this repository.

Microsoft connector documentation:
https://learn.microsoft.com/power-query/connectors/postgresql

## Model setup

Create and validate the relationships first using [`relationship_checklist.md`](relationship_checklist.md).

Then apply the remaining field configuration in [`model_spec.md`](model_spec.md).

After the tables and relationships exist, apply and validate the measures using [`measure_validation_checklist.md`](measure_validation_checklist.md).

The checklist uses:

```text
TMDLScripts/01_measures.tmdl
```

The script adds the measures defined in `docs/kpi_definitions.md` and validates them against the SQL/full-dataset totals before any report page is built.

Microsoft TMDL view documentation:
https://learn.microsoft.com/power-bi/transform-model/desktop-tmdl-view

## Report design

The report is intentionally limited to three pages:

1. Executive Overview
2. Customer Analysis
3. Product & Cancellation Analysis

The visual and interaction specification is documented in [`dashboard_spec.md`](dashboard_spec.md).

## Source control

The repository keeps the semantic-model specification and TMDL scripts as text.

When the report is created and validated in Power BI Desktop, it can be saved as a Power BI Desktop project (PBIP) with TMDL model metadata for finer-grained source control. Local cache and machine-specific `.pbi` files are excluded by `.gitignore`.

Microsoft Power BI project documentation:
https://learn.microsoft.com/power-bi/developer/projects/projects-dataset
