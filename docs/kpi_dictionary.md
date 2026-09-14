# KPI Dictionary

RetailIQ treats KPI definitions as version-controlled business logic. A dashboard measure is not considered complete until its inclusion/exclusion rules are documented.

## Event rules

The warehouse classifies source lines before aggregation:

- `sale`: non-cancellation line with quantity > 0 and unit price > 0
- `cancellation`: cancellation-coded invoice or negative quantity
- `non_revenue`: remaining records retained for audit/data-quality analysis

No event class is physically removed from the fact table.

## Executive KPIs

| KPI | Definition | Grain / caveat |
|---|---|---|
| Gross sales value | Sum of `line_value` for `sale` events. | Sales value before cancellations. Not profit; source cost data is unavailable. |
| Cancellation value | Sum of `ABS(line_value)` for `cancellation` events. | Reported separately so return/cancellation exposure remains visible. |
| Net sales value | Gross sales value - cancellation value. | A commercial reporting measure; source row/value preservation is reconciled separately. |
| Orders | Distinct invoice numbers containing `sale` events. | Invoice-level metric. |
| Average order value | Gross sales value / orders. | Uses sale orders; cancellation value is shown separately rather than allocated retrospectively to an original order. |
| Units sold | Sum of quantity for `sale` events. | Cancellation quantities are not mixed into this measure. |
| Active customers | Distinct non-null customers with at least one `sale` event in the selected period. | Anonymous purchases can contribute to sales but not customer counts. |
| Repeat-customer rate | Customers with >=2 sale orders / customers with >=1 sale order. | Requires non-null customer ID. |
| Cancellation orders | Distinct invoice numbers classified as cancellation events. | This is not a matched-return rate; the source does not provide an explicit original-order foreign key. |

## Customer analytics

| KPI | Definition |
|---|---|
| First purchase date | Earliest `sale` event date per customer. |
| Last purchase date | Most recent `sale` event date per customer. |
| Recency | Days between the dataset's most recent sale date and the customer's last purchase date. |
| Frequency | Distinct sale orders per customer. |
| Monetary value | Customer gross sales value - customer cancellation value. |
| Cohort month | Calendar month of the customer's first sale order. |
| Cohort retention | Distinct cohort customers active in a later month / customers in the original cohort. |
| RFM score | Quintile scores for recency, frequency and monetary value. | Scores are relative to this dataset population, not universal customer-value thresholds. |

## Product analytics

| KPI | Definition |
|---|---|
| Product gross sales value | Gross sale-event value grouped by stock code. |
| Product net sales value | Product gross sales value - product cancellation value. |
| Product units | Sale-event quantity grouped by stock code. |
| Sales orders | Distinct sale invoices containing the product. |
| Customer reach | Distinct known customers buying the product. |
| Cancellation exposure | Absolute cancellation value for the stock code. |

## Geographic analytics

| KPI | Definition |
|---|---|
| Country gross sales | Gross sale-event value by source country. |
| Country net sales | Country gross sales - cancellation value. |
| Country orders | Distinct sale invoices by country. |
| Country customers | Distinct known sale customers by country. |

## Data-quality KPIs

The dashboard/audit layer can surface:

- missing customer IDs
- missing descriptions
- non-positive quantity rows
- non-positive unit-price rows
- cancellation rows
- repeated exact rows
- source-to-fact row-count difference
- source-to-fact line-value difference

## Guardrails

- Currency is GBP because the source documents unit price in sterling.
- No profit, gross margin, CAC, marketing ROI or CLV is presented without source fields that support it.
- Cancellation value is not claimed to be a perfectly matched return against an original invoice because the source does not expose a reliable original-order foreign key.
- Exact repeated rows are flagged but not deleted without evidence that they are ingestion errors.
- A metric shown in Power BI must map to warehouse SQL or a documented DAX measure.
- Where business interpretation is uncertain, uncertainty is surfaced rather than silently encoded.
