# Product classification

The source `StockCode` field is not limited to merchandise.

The full-dataset validation showed that the same column also contains postage, carriage, platform fees, bank charges, commissions, accounting adjustments, discounts, samples, gift vouchers and test records. Treating every stock code as a sellable product makes product rankings misleading.

The analytical product dimension therefore includes a deterministic `product_type`.

## Classification rules

| Product type | Stock-code rule | Examples |
| --- | --- | --- |
| `shipping` | Explicit shipping/carriage codes | `DOT`, `POST`, `C2` |
| `fee` | Explicit fee/commission codes | `AMAZONFEE`, `BANK CHARGES`, `CRUK` |
| `adjustment` | Explicit accounting/manual adjustment codes | `B`, `M`, `ADJUST`, `ADJUST2` |
| `discount` | Explicit discount code | `D` |
| `sample` | Explicit sample code | `S` |
| `voucher` | Stock codes beginning with `gift_` | `gift_0001_30` |
| `test` | Stock codes beginning with `TEST` | `TEST001` |
| `merchandise` | Every other identified stock code | `22423`, `DCGS0076`, `PADS` |
| `unknown` | Missing stock code | Unknown dimension member |

## Why the rule is explicit

The project does **not** classify every non-numeric stock code as operational.

The real dataset contains alphabetic or alphanumeric stock codes that represent ordinary merchandise. A broad regular expression would incorrectly remove products such as `DCGS0076` and `PADS` from product analysis.

Operational categories are therefore assigned only where the code semantics are clear from the full-dataset profile.

## Analytical behaviour

All transaction lines remain in `analytics.fact_sales`.

This means shipping, fees, discounts and adjustments still contribute to overall net revenue and other whole-business measures.

Only **merchandise product rankings** apply:

```text
dim_product[product_type] = 'merchandise'
```

A separate operational-code query keeps the excluded product-ranking values visible:

```text
sql/analysis/07_operational_stock_codes.sql
```

This separation avoids hiding economically relevant entries while preventing operational charges from being described as top-selling products.
