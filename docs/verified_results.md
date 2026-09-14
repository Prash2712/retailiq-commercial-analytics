# Verified results

This file contains only metrics reproduced by the automated **Full data audit** workflow against the complete UCI Online Retail II source. It is the evidence base for README, dashboard and CV claims.

## Audit scope

- Source: UCI Online Retail II, DOI `10.24432/C5CG6D`
- Source period: 1 December 2009 to 9 December 2011
- Pipeline: official UCI download -> typed Parquet -> PostgreSQL staging -> star schema -> commercial marts -> reconciliation
- Verified workflow run: `34874874732`
- Workflow URL: `https://github.com/Prash2712/retailiq-commercial-analytics/actions/runs/34874874732`

## Source and quality profile

| Metric | Verified value |
|---|---:|
| Transaction lines | 1,067,371 |
| Exact repeated business rows | 34,335 |
| Missing customer ID rows | 243,007 |
| Missing descriptions | 4,382 |
| Non-positive quantity rows | 22,950 |
| Non-positive unit-price rows | 6,207 |
| Cancellation rows | 19,494 |

Exact repeated business rows are identified using the transaction attributes rather than source-lineage fields. They are **flagged, not silently deleted**.

## Warehouse reconciliation

| Check | Staging | Fact | Difference |
|---|---:|---:|---:|
| Row count | 1,067,371 | 1,067,371 | 0 |
| Raw line-value total | £19,287,250.5680 | £19,287,250.5680 | £0.0000 |

The warehouse build fails if either reconciliation difference is non-zero.

## Commercial profile

| Metric | Verified value |
|---|---:|
| Gross sales value | £20,972,594.5680 |
| Cancellation value | £1,527,415.0000 |
| Net sales value | £19,445,179.5680 |
| Sale orders | 40,077 |
| Cancellation-order events | 11,685 |
| Net sales per sale order | £485.20 |
| Known customers | 5,878 |
| Repeat customers | 4,255 |
| Repeat-customer rate | 72.39% |
| Products | 5,304 |
| Countries | 43 |

### Derived context

- Cancellation value is **7.28% of gross sales value**.
- Net sales retain **92.72% of gross sales value** after the cancellation treatment used by this project.
- Rows without a customer ID are **22.77% of source transaction lines**; customer-level analytics therefore cover a smaller population than transaction-level sales analytics.
- Exact repeated business rows represent **3.22% of source rows**. They are surfaced as a data-quality condition because the dataset does not provide enough evidence to assume every repeated line is erroneous.

## Interpretation guardrails

1. `gross sales value`, `cancellation value` and `net sales value` are analytical definitions for this project; they are not accounting revenue recognition.
2. The source provides unit selling prices but no product costs. Profit, gross margin, CAC and ROI are therefore not reported.
3. Missing customer IDs are excluded only from customer-level metrics that require identity; they do not automatically invalidate transaction-level sales analysis.
4. Cancellation invoices are treated explicitly and kept visible rather than removed from the source.
5. No result in this file should be changed manually. If business logic changes, rerun the full-data audit and update this evidence file from the resulting output.
