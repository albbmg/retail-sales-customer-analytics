# Findings

This document summarises the main observations from the validated **Online Retail II** analytical model.

All figures come from the complete UCI source dataset after the raw → clean → staging → analytics pipeline completed successfully and all analytical data-quality checks passed.

The analysis is descriptive. It does not infer causality, profitability or customer intent beyond what the transaction data supports.

## 1. Overall activity

Across the complete source period, from **1 December 2009 to 9 December 2011**, the model contains:

- **£19.29M** net revenue;
- **45,336** non-cancellation sales orders;
- **11.67M** units sold;
- **5,881** active identified customers;
- **£459.10** average order value.

Non-cancellation revenue is **£20.81M**. The signed difference between non-cancellation and net revenue is **£1.53M**, reflecting the financial effect of cancellation invoices retained in the model.

The cancellation invoice rate is **15.46%** of distinct invoice records.

This rate describes the share of invoice numbers flagged as cancellations. It is not a matched-order cancellation probability because cancellation invoices are represented separately in the source.

**Reproducible from:** `sql/analysis/01_kpi_overview.sql`

## 2. Comparable 2010–2011 trading periods

The source ends on **9 December 2011**, so a full-calendar-year comparison would be misleading. I therefore compare **January-November 2010** with **January-November 2011**.

| Metric | 2010 Jan-Nov | 2011 Jan-Nov | Change |
| --- | ---: | ---: | ---: |
| Net revenue | £8.36M | £8.57M | +2.43% |
| Sales orders | 21,343 | 19,496 | -8.65% |
| Units sold | 5.38M | 4.98M | -7.42% |
| Active customers | 4,154 | 4,174 | +0.48% |
| Average order value | £417.22 | £470.97 | +12.88% |
| Cancellation invoice rate | 15.97% | 14.72% | -1.25 pp |

Within these comparable periods, net revenue increased slightly while order volume declined. The same period also shows a materially higher average order value.

That combination is consistent with higher revenue per non-cancellation order in 2011, but the transaction data alone does not explain **why** average order value changed.

**Reproducible from:** `sql/analysis/08_comparable_periods.sql`

## 3. Revenue is concentrated in the later months of the year

The five highest-revenue **complete** months are:

| Month | Net revenue | Sales orders | Active customers | Average order value |
| --- | ---: | ---: | ---: | ---: |
| November 2011 | £1.46M | 3,021 | 1,665 | £499.67 |
| November 2010 | £1.42M | 3,093 | 1,607 | £475.35 |
| December 2010 | £1.13M | 1,699 | 885 | £743.14 |
| October 2011 | £1.07M | 2,275 | 1,364 | £507.68 |
| October 2010 | £1.05M | 2,489 | 1,497 | £452.61 |

October and November appear among the strongest months in both complete annual periods available in the dataset. This is evidence of a repeated late-year concentration **within this two-year sample**, not enough evidence to claim a general seasonal law.

December 2011 is deliberately excluded because only nine days of that month are present.

**Reproducible from:** `sql/analysis/02_monthly_sales.sql` and `src/retail_analytics/study_summary.py`

## 4. Customer revenue is concentrated, but not dominated by a single account

For customers that can be identified and qualify as active, total net revenue is **£16.71M**.

Revenue concentration within that population is:

- top customer: **£598.22K**, or **3.58%**;
- top 10 customers: **£2.71M**, or **16.19%**;
- top 100 customers: **£6.13M**, or **36.67%**.

The largest customer is economically important, but the identified-customer revenue base is not dependent on one account alone. Even the top 100 customers account for well under half of identified active-customer net revenue.

This interpretation applies only to identified customers. A material portion of source transactions has no customer identifier and is analysed separately.

**Reproducible from:** `sql/analysis/09_customer_concentration.sql`

## 5. Geographic revenue is highly concentrated in the United Kingdom

The United Kingdom contributes **£16.38M**, representing **84.94%** of total net revenue.

The five highest-revenue countries together account for **94.84%**.

The next largest markets by net revenue are:

1. EIRE — **£615.52K**
2. Netherlands — **£548.52K**
3. Germany — **£417.99K**
4. France — **£328.19K**

The dataset is therefore strongly centred on the UK market. Cross-country comparisons should be read in that context rather than as observations from a geographically balanced customer base.

**Reproducible from:** `sql/analysis/05_country_performance.sql` and `sql/analysis/10_geographic_concentration.sql`

## 6. Missing customer identifiers materially limit customer-level analysis

The source contains **243,007 transaction lines without Customer ID**, representing **22.77%** of all lines.

Those rows account for:

- **£2.64M** net revenue;
- **13.68%** of total net revenue;
- **8,361** non-cancellation invoice numbers.

These transactions are retained in the fact table through the explicit `Unknown customer` dimension member, so overall sales measures remain complete.

They are excluded from active-customer counts and customer rankings because assigning them to known customers would require unsupported assumptions.

This coverage gap is one of the main limitations of any customer-level conclusion drawn from the dataset.

**Reproducible from:** `sql/analysis/11_unknown_customer_impact.sql`

## 7. Merchandise dominates activity, while operational codes have material financial impact

After validating the complete dataset, I found that `StockCode` contains both merchandise and operational records.

The analytical product dimension therefore separates these categories explicitly.

| Product type | Lines | Net revenue | Cancellation value |
| --- | ---: | ---: | ---: |
| Merchandise | 1,061,465 | £19.38M | £726.56K |
| Shipping | 3,850 | £448.37K | £15.56K |
| Fee | 161 | -£304.26K | £338.80K |
| Adjustment | 1,497 | -£222.84K | £425.58K |
| Discount | 177 | -£13.48K | £13.88K |
| Sample | 104 | -£6.07K | £6.20K |
| Voucher | 100 | £1.69K | £69.56 |
| Test | 17 | £203.50 | £22.50 |

Operational entries are economically relevant and therefore remain in overall revenue measures.

They are excluded only from merchandise rankings. Without this separation, entries such as `DOTCOM POSTAGE` and `POSTAGE` incorrectly appear among the highest-revenue "products".

**Reproducible from:** `sql/analysis/12_product_type_impact.sql`, `sql/analysis/07_operational_stock_codes.sql`, and `docs/product_classification.md`

## 8. Highest-revenue merchandise products

After separating operational stock codes, the leading merchandise products by net revenue are:

| Product | Net revenue | Sales orders | Units sold |
| --- | ---: | ---: | ---: |
| REGENCY CAKESTAND 3 TIER | £327.81K | 3,931 | 27,594 |
| CREAM HANGING HEART T-LIGHT HOLDER | £253.72K | 5,373 | 100,152 |
| JUMBO BAG RED RETROSPOT | £181.28K | 3,995 | 98,356 |
| PARTY BUNTING | £147.95K | 2,679 | 28,426 |
| ASSORTED COLOUR BIRD ORNAMENT | £131.41K | 2,810 | 81,817 |

Revenue ranking and unit-volume ranking are not interchangeable. For example, the leading product by revenue is not the product with the highest unit volume among these items.

The analysis therefore keeps both net revenue and units sold available rather than using one as a proxy for the other.

**Reproducible from:** `sql/analysis/04_product_performance.sql`

## 9. Cancellation and adjustment records should remain visible

Cancellation invoices and negative adjustments are preserved throughout the pipeline.

This matters for two reasons:

1. removing them during cleaning would overstate net revenue;
2. operational codes show that some negative financial entries are accounting or fee-related rather than merchandise returns.

The analysis therefore keeps:

- signed net revenue;
- non-cancellation revenue;
- cancellation invoice counts;
- cancellation value;
- operational-code impact

as separate concepts.

This preserves the source economics without implying that every negative line represents the same business event.

**Reproducible from:** `sql/analysis/06_cancellation_trend.sql`, `sql/analysis/07_operational_stock_codes.sql`, and `docs/kpi_definitions.md`

## Interpretation boundaries

The findings above should be read with the following constraints:

- the data covers one retailer and a historical period from 2009 to 2011;
- December 2011 is incomplete;
- product costs are unavailable, so revenue is not profit;
- 22.77% of transaction lines have no customer identifier;
- cancellation invoices are separate records and are not matched back to original sales orders;
- operational stock codes are part of the financial record but are not merchandise;
- observed changes and concentrations are descriptive and should not be interpreted as causal relationships.

These constraints are kept visible because they materially affect what can and cannot be concluded from the data.
