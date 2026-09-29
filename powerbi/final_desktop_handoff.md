# Power BI Desktop final handoff

This is the final preparation step before the report can be considered complete.

The repository already defines the semantic model, measures, three report pages and cross-page consistency rules. This checklist is the point where those specifications must be verified in **Power BI Desktop**.

Do not mark the Power BI report complete until every section below has been checked in Desktop.

## 1. Refresh the model

Open the report/project in Power BI Desktop.

Confirm the local PostgreSQL environment is running:

```bash
docker compose up -d --wait postgres
```

Refresh the Power BI model.

The refresh must complete without:

- credential errors;
- missing-table errors;
- relationship errors;
- DAX errors;
- Power Query errors.

If the local PostgreSQL database has been reset, rebuild the analytical model before refreshing Power BI.

## 2. Clear all filters

Before validating headline values:

- clear Date slicers;
- clear Country slicers;
- clear Product slicers;
- clear visual selections;
- confirm there are no unexpected page-level filters;
- confirm there are no unexpected report-level filters.

Use this clean state for the headline validation.

## 3. Validate headline measures

The unfiltered model must reproduce:

| Measure | Expected value |
| --- | ---: |
| Net Revenue | £19,287,250.57 |
| Non-Cancellation Revenue | £20,813,918.43 |
| Sales Orders | 45,336 |
| Units Sold | 11,672,569 |
| Average Order Value | £459.10 |
| Active Customers | 5,881 |
| Net Revenue per Active Customer | £2,841.24 |
| Cancellation Invoices | 8,292 |
| Total Invoices | 53,628 |
| Cancellation Invoice Rate | 15.46% |
| Cancellation Value | £1,526,667.86 |

If a value differs materially:

1. inspect slicers and filters;
2. inspect relationship direction;
3. confirm the versioned measure is being used;
4. compare against `docs/kpi_definitions.md`;
5. do not change DAX merely to make the card match.

## 4. Validate the three pages

### Executive Overview

Confirm:

- all five KPI cards match;
- United Kingdom leads Net Revenue by Country;
- merchandise ranking excludes operational codes;
- November 2011 is the strongest complete month by Net Revenue;
- December 2011 is labelled as partial.

### Customer Analysis

Confirm:

- Active Customers = 5,881;
- Net Revenue per Active Customer = £2,841.24;
- Customer 18102 leads the customer ranking;
- Unknown customer does not appear in customer-level visuals;
- the missing-Customer-ID note is visible.

### Product & Cancellation Analysis

Confirm:

- Units Sold = 11,672,569;
- Cancellation Invoices = 8,292;
- Cancellation Value = £1,526,667.86;
- REGENCY CAKESTAND 3 TIER leads merchandise Net Revenue;
- operational entries remain in their dedicated table;
- operational entries do not appear in merchandise rankings;
- cancellation count and value use clearly separate scales.

## 5. Validate interactions

On each page:

- test Date slicer;
- test Country slicer;
- test one chart selection;
- clear the selection;
- confirm the page returns to the expected unfiltered state.

On Product & Cancellation Analysis, also test the Product slicer.

No selection should silently change the definition of a KPI.

## 6. Validate presentation

Run `final_consistency_checklist.md`.

Pay particular attention to:

- page titles;
- consistent slicer placement;
- KPI-card formatting;
- monetary and percentage formats;
- December 2011 partial-period note;
- alt text;
- tab order;
- text contrast;
- absence of raw database field names.

## 7. Save the report

Save the validated report after the refresh and review pass.

Preferred source-control approach:

- use a Power BI project format when available in the installed Desktop version;
- keep model/report source files under `powerbi/`;
- do not commit credentials;
- do not commit local Power BI cache/state files;
- keep the existing `.gitignore` rules intact.

Do not claim the report is complete in the root README until the saved project has been reopened successfully.

## 8. Reopen check

Close Power BI Desktop.

Reopen the saved report/project.

Confirm:

- the project opens without repair prompts;
- all three pages exist;
- the five analytical tables are present;
- relationships remain active;
- measures remain available;
- visual formatting persists.

This simple reopen check catches an impressive number of avoidable human inventions.

## 9. Capture final screenshots

Create one clean screenshot per page with:

- all slicers cleared;
- no visual selected;
- full page visible;
- consistent Desktop zoom;
- no open filter, data or formatting panes;
- no credentials or machine-specific information visible.

Use these filenames:

```text
docs/images/powerbi-executive-overview.png
docs/images/powerbi-customer-analysis.png
docs/images/powerbi-product-cancellation-analysis.png
```

The screenshots should show the report itself, not Power BI setup dialogs.

## 10. Screenshot validation

Before committing screenshots, confirm:

- text is readable at GitHub preview size;
- no visual is clipped;
- page titles are visible;
- KPI values are visible;
- slicers are in their default state;
- no hover tooltip is covering a visual;
- no selection highlight is active.

## 11. Repository completion

Only after the Desktop validation and screenshots succeed:

- add the three screenshots;
- link them from the root README;
- mark the Power BI roadmap item complete;
- close issue #35.

## Stop point

If any Desktop value, relationship or visual fails validation, stop and fix that specific problem before screenshots or README completion.

A screenshot is evidence of the validated report, not a substitute for validation.
