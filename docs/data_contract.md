# Data Contract

## Source

**Dataset:** UCI Online Retail II  
**Dataset ID:** 502  
**DOI:** 10.24432/C5CG6D  
**Coverage:** 1 Dec 2009 to 9 Dec 2011  
**Source type:** Excel workbook distributed in a ZIP archive

The source is a real transaction dataset for a UK-based non-store retailer. Raw source files are downloaded by the pipeline and are intentionally excluded from Git.

## Grain

One row represents one invoice line: a product (`stock_code`) recorded on an invoice (`invoice_no`) at a timestamp (`invoice_date`). Multiple rows can therefore share the same invoice number.

## Normalised fields

| Field | Type | Meaning |
|---|---|---|
| `invoice_no` | string | Invoice identifier. Prefix `C` indicates cancellation in the source documentation. |
| `stock_code` | string | Product/item code. |
| `description` | string | Product description. May be missing. |
| `quantity` | numeric | Item quantity on the invoice line. Negative values require interpretation rather than silent deletion. |
| `invoice_date` | datetime | Transaction date/time. |
| `unit_price` | numeric | Unit price in GBP. |
| `customer_id` | string | Customer identifier. May be missing. |
| `country` | string | Customer country. |
| `source_sheet` | string | Workbook sheet from which the row originated. Added for lineage. |
| `is_cancellation` | boolean | Derived from an invoice number beginning with `C`. |
| `line_value` | numeric | `quantity * unit_price`; not automatically equivalent to recognised net revenue. |

## Data-quality principles

RetailIQ separates **observation** from **business-rule exclusion**. Rows are not deleted merely because they appear inconvenient.

The profiling layer records at minimum:

- exact duplicate rows
- missing invoice number
- missing stock code
- missing description
- missing customer ID
- missing invoice timestamp
- non-positive quantity
- non-positive unit price
- cancellation rows

Later warehouse transformations must document which records are included in each KPI and why.

## Known interpretation risks

1. Cancellation invoices and negative quantities need explicit treatment in net-sales logic.
2. Missing customer IDs prevent customer-level retention analysis for those rows but do not automatically invalidate transaction-level revenue analysis.
3. The dataset has sales prices but no product cost or cost-to-serve fields. **Gross margin and profit must not be inferred.**
4. Duplicate-looking rows can be legitimate repeated line items; exact duplicates are flagged before any deduplication policy is applied.
5. Product descriptions can change or be missing, so `stock_code` is the stronger product key candidate.

## Reproducibility

Running `retailiq ingest` downloads the official UCI archive, calculates SHA-256 hashes for the archive and extracted workbook, stores provenance locally, reads every workbook sheet, applies the schema contract, and writes the normalised dataset to Parquet.
