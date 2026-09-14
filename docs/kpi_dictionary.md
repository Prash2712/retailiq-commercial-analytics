# KPI Dictionary

RetailIQ treats KPI definitions as version-controlled business logic. A dashboard measure is not considered complete until its inclusion/exclusion rules are documented.

## Executive KPIs

| KPI | Definition | Grain / caveat |
|---|---|---|
| Gross sales value | Sum of positive `quantity * unit_price` on non-cancellation sales lines that pass the agreed sales-validity rules. | Not profit. Cost data is unavailable. |
| Cancellation value | Absolute value of cancellation/negative sales lines under the documented cancellation logic. | Report separately from sales rather than hiding it. |
| Net sales value | Gross sales value less validated cancellation/return value. | Final SQL implementation will be reconciled against source totals. |
| Orders | Distinct valid non-cancellation invoice numbers. | Invoice-level metric. |
| Average order value | Net sales value / valid orders. | Must use a consistent order population. |
| Units sold | Sum of positive quantities for valid sale lines. | Returns/cancellations reported separately. |
| Active customers | Distinct non-null customer IDs with at least one valid order in the selected period. | Anonymous purchases excluded from customer counts only. |
| Repeat-customer rate | Customers with >=2 valid orders / customers with >=1 valid order. | Requires non-null customer ID. |
| Cancellation rate | Cancelled orders / all identifiable order events under the final cancellation matching policy. | Definition will be frozen after source exploration. |

## Customer analytics

| KPI | Definition |
|---|---|
| First purchase date | Earliest valid order date per customer. |
| Recency | Days between analysis reference date and most recent valid purchase. |
| Frequency | Distinct valid orders per customer. |
| Monetary value | Net sales value attributable to the customer. |
| Cohort month | Calendar month of the customer's first valid purchase. |
| Cohort retention | Share of cohort customers returning in each subsequent cohort period. |

## Product analytics

| KPI | Definition |
|---|---|
| Product sales value | Net sales value grouped by stock code. |
| Product units | Net valid quantity grouped by stock code. |
| Revenue concentration | Share of net sales represented by top-N products. |
| Cancellation exposure | Cancellation/return value grouped by stock code relative to its gross sales where meaningful. |

## Guardrails

- Currency is GBP because the source documents unit price in sterling.
- No profit, gross margin, CAC, marketing ROI or CLV assumptions will be presented without source fields that support them.
- A metric shown in Power BI must map to either warehouse SQL or a documented DAX measure.
- Where business interpretation is uncertain, the uncertainty is surfaced rather than silently encoded.
