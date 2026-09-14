# RetailIQ executive insight memo

## Purpose

This memo translates the currently verified full-source metrics into management-level implications. It intentionally limits conclusions to evidence already reproduced by the automated audit. Product-, geography- and cohort-specific recommendations will be added only after those slices are rendered and reviewed in the BI report.

## Executive summary

The analysed source contains **1,067,371 transaction lines** covering 1 December 2009 to 9 December 2011. Under RetailIQ's documented sales/cancellation rules, the data produces **£20.97m gross sales value**, **£1.53m cancellation value** and **£19.45m net sales value** across **40,077 sale orders**.

The strongest immediately visible commercial signal is customer recurrence: **4,255 of 5,878 known purchasing customers are repeat customers**, a **72.39% repeat-customer rate**. This makes retention and customer-value segmentation more decision-relevant than a portfolio that focuses only on top-line sales.

The largest analytical constraint is identity coverage. **243,007 rows (22.77%) lack a customer ID**, so transaction-level commercial reporting has broader coverage than customer-level retention/RFM analysis. Management should therefore treat customer metrics as metrics for the identifiable-customer population rather than the full transaction population.

## Key observations

### 1. Cancellation exposure is commercially material

Cancellation value is **£1.53m**, equivalent to **7.28% of gross sales value** under the project's event-classification rules. That is large enough to keep cancellations visible as a first-class KPI rather than netting them away without explanation.

**Management question for the dashboard:** Is cancellation exposure concentrated in particular products, periods, countries or customer segments?

### 2. Repeat purchasing is a major feature of the identifiable customer base

The verified repeat-customer rate is **72.39%**. This supports deeper cohort and RFM analysis because a substantial majority of identifiable customers have more than one valid sale order.

**Management question for the dashboard:** Which cohorts and RFM segments account for the largest share of repeat purchasing and net sales?

### 3. Customer analytics have a material coverage limitation

Rows with no customer identifier represent **22.77% of source transaction lines**. Those records remain valid for many transaction/product/geography analyses but cannot be assigned reliably to a customer journey.

**Management implication:** Every customer-focused page should disclose its population basis. Do not compare customer metrics with transaction-level metrics as though they cover identical populations.

### 4. Repeated rows need governance, not automatic deletion

The full source contains **34,335 repeated business rows (3.22%)**. RetailIQ flags repeated occurrences but preserves them in the reconciled fact table because the source does not prove that each repetition is an erroneous duplicate.

**Management implication:** Dashboard totals remain reconciled to the source. A separate data-quality view allows users to quantify the repeated-row exposure rather than silently changing the business record.

## Decision framework for the BI report

The executive dashboard should answer four decisions in sequence:

1. **Performance:** What happened to net sales, order volume, AOV and cancellations over time?
2. **Customer:** Is performance being driven by repeat customers, specific cohorts or high-value RFM groups?
3. **Concentration:** Which products and countries contribute most to sales and cancellation exposure?
4. **Trust:** Are data-quality conditions large enough to change interpretation of the preceding views?

## What is deliberately not claimed

- No profit or gross-margin statement: product cost is not present in the source.
- No causal claim that repeat customers caused sales growth.
- No claim that every repeated row is erroneous.
- No marketing attribution, CAC or campaign ROI: acquisition-channel and marketing-spend fields are absent.
- No recommendation to remove products/countries until concentration and cancellation slices are reviewed in the finished report.

## Evidence reference

All figures above are reproduced in [`verified_results.md`](verified_results.md) and by the repository's Full data audit workflow.
