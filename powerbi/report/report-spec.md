# RetailIQ report specification

The report is designed for a commercial manager reviewing performance, customer behaviour, concentration risk and data trust. Use native Power BI visuals only.

## Global design

- Canvas: 16:9 widescreen.
- Page navigation: Executive | Customer | Product | Geography | Data Quality.
- Global slicers where relevant: Date, Country.
- Product/customer-specific slicers belong only on their own pages.
- All money measures use GBP formatting.
- Use measure-driven titles where useful; avoid decorative text that repeats labels.
- Keep the report information-dense but not crowded: one clear decision question per visual.
- Do not display profit, margin, CAC or ROI.

## Page 1 — Executive overview

### Decision question

**What happened commercially, and is the change driven by sales volume, order economics or cancellations?**

### Top KPI strip

1. **Net Sales Value** — card — `[Net Sales Value]`
2. **Sale Orders** — card — `[Sale Orders]`
3. **Average Order Value** — card — `[Average Order Value]`
4. **Known Customers** — card — `[Known Customers]`
5. **Repeat Customer Rate** — card — `[Repeat Customer Rate]`
6. **Cancellation Value %** — card — `[Cancellation Value %]`

Full-source validation targets (with no slicers):

- Net Sales Value: £19,445,179.5680
- Sale Orders: 40,077
- Average Order Value: ~£485.20
- Known Customers: 5,878
- Repeat Customer Rate: 72.39%
- Cancellation Value %: 7.28%

### Main visuals

**A. Net sales trend**
- Visual: line chart
- X: `Date[Year Month]`
- Y: `[Net Sales Value]`
- Tooltip: `[Gross Sales Value]`, `[Cancellation Value]`, `[Sale Orders]`, `[Average Order Value]`
- Purpose: show direction, seasonality and periods that require drill-down.

**B. Gross-to-net bridge**
- Visual: waterfall
- Categories: Gross Sales, Cancellation Value, Net Sales
- Use the governed measures; cancellation is the negative step.
- Purpose: make the difference between gross and net visible rather than hiding it in a single number.

**C. Orders vs AOV**
- Visual: combo chart
- X: `Date[Year Month]`
- Columns: `[Sale Orders]`
- Line: `[Average Order Value]`
- Purpose: separate volume-led and basket-value-led movement.

**D. Country contribution**
- Visual: horizontal bar
- Category: `Geography[Country]`
- Value: `[Net Sales Value]`
- Top N: 10 by `[Net Sales Value]`
- Purpose: show concentration without forcing a map where comparison is the primary task.

### Interaction

- Country bar cross-filters trend and KPI cards.
- Date slicer filters all visuals on the page.
- Do not allow the waterfall to cross-filter the page; it is explanatory, not a dimension selector.

---

## Page 2 — Customer & retention

### Decision question

**Which identifiable customers return, and how durable is retention across acquisition cohorts?**

### KPI strip

1. `[Identifiable Purchasing Customers]`
2. `[Repeat Customers]`
3. `[Repeat Customer Rate]`
4. Median/typical recency should be added only if implemented as a governed measure.

### Main visuals

**A. Cohort-retention matrix**
- Visual: matrix
- Rows: `Cohort Retention[Cohort Month]`
- Columns: `Cohort Retention[Months Since First Purchase]`
- Values: `MAX(Cohort Retention[Retention Rate])`
- Conditional formatting: sequential heat scale.
- Purpose: show whether newer/older customer cohorts return in subsequent months.

**B. RFM customer scatter**
- Visual: scatter
- X: `Customer RFM[Recency Days]`
- Y: `Customer RFM[Monetary Value]`
- Size: `Customer RFM[Frequency]`
- Details: `Customer RFM[Customer ID]`
- Tooltip: RFM scores.
- Purpose: distinguish recent high-value repeat customers from lapsed/high-value or low-frequency customers.

**C. Repeat vs one-time customers**
- Visual: 100% stacked bar or donut only if labels remain readable.
- Category: `Customer Summary[Is Repeat Customer]`
- Value: count of customer rows.
- Purpose: communicate the population split quickly.

**D. Customer order-frequency distribution**
- Visual: column chart
- X: `Customer Summary[Order Count]` binned to a sensible upper bound; group extreme values as `20+` if needed.
- Y: count of customers.
- Purpose: show that the repeat-rate headline can conceal highly skewed frequency.

### Required disclosure

Add a small information note:

> Customer-level analytics use identifiable customer IDs. 243,007 transaction lines (22.77% of the source) have no customer ID and cannot be assigned reliably to a customer journey.

---

## Page 3 — Product performance

### Decision question

**Which products drive sales, and where is cancellation exposure concentrated?**

### KPI strip

1. Distinct products (`5,304` full source)
2. `[Top 10 Product Share]`
3. `[Net Sales Value]`
4. `[Cancellation Value]`

### Main visuals

**A. Top products by net sales**
- Visual: horizontal bar
- Category: `Product[Product Description]`
- Value: `[Net Sales Value]`
- Top N: 15.
- Tooltip: Stock Code, Units Sold, Gross Sales Value, Cancellation Value, Sale Orders.

**B. Product concentration / Pareto**
- Visual: ranked product bar/line view.
- At minimum show top-N net sales plus `[Top 10 Product Share]` card.
- Do not label this as an 80/20 result unless the data actually supports that threshold.

**C. Cancellation exposure**
- Visual: scatter
- X: `[Gross Sales Value]`
- Y: `[Cancellation Value]`
- Details: `Product[Stock Code]`
- Tooltip: Product Description, Net Sales Value, Units Sold.
- Purpose: find high-volume/high-cancellation products rather than ranking on cancellations alone.

**D. Product detail table**
- Columns: Stock Code, Product Description, Gross Sales, Cancellation Value, Net Sales, Units Sold, Sale Orders.
- Conditional formatting only on cancellation value/share.

---

## Page 4 — Geography

### Decision question

**How concentrated are sales across countries, and which markets combine scale with cancellation exposure?**

### Main visuals

**A. Ranked country performance**
- Visual: horizontal bar
- Category: `Geography[Country]`
- Value: `[Net Sales Value]`
- Sort descending.

**B. Country scale vs cancellation exposure**
- Visual: scatter
- X: `[Net Sales Value]`
- Y: `[Cancellation Value]`
- Size: `[Sale Orders]`
- Details: `Geography[Country]`

**C. Geographic map**
- Visual: native Power BI map, only if geocoding is unambiguous.
- Location: `Geography[Country]`
- Size: `[Net Sales Value]`
- Tooltip: Sale Orders, Known Customers, Cancellation Value %.
- If Power BI reports ambiguous geocoding, remove the map and keep the ranked comparison visuals.

**D. Country detail table**
- Country, Net Sales, Sale Orders, Known Customers, Cancellation Value, Cancellation Value %.

---

## Page 5 — Data quality & reconciliation

### Decision question

**Can management trust the totals, and what source conditions affect interpretation?**

### Validation cards

1. `[Fact Row Count]` — expected 1,067,371
2. `[Repeated Exact Rows]` — expected 34,335
3. `[Missing Customer ID Rows]` — expected 243,007
4. `Reconciliation[Row Count Difference]` — expected 0
5. `Reconciliation[Line Value Difference]` — expected £0.0000

### Main visuals

**A. Data-quality issue counts**
- Visual: horizontal bar
- Category: `Data Quality[Metric]`
- Value: `Data Quality[Value]`
- Exclude `source_rows` from the bar or show it separately so it does not compress the remaining issues.

**B. Quality issue rates**
- Create display measures only where the denominator is explicit (usually source rows).
- Show repeated-row and missing-customer-ID rates as the primary percentages.

**C. Reconciliation table**
- Show staging vs fact row count and line-value totals with difference columns.
- Use conditional formatting: only zero differences are acceptable.

### Required methodology note

> Repeated business rows are flagged rather than automatically removed. Missing customer IDs are excluded only from customer-identity analyses. The fact table preserves the source row population and reconciles to source line value.

---

## Drill-through and tooltips

### Product drill-through

Target fields: Product Stock Code / Product Description.

Show:
- monthly net sales trend
- gross vs cancellation value
- units sold
- sale orders
- customer count

### Country drill-through

Target field: Country.

Show:
- monthly net sales trend
- sale orders
- known customers
- cancellation value %
- top products in the selected country

## Accessibility and usability checks

- Every chart needs a descriptive title that states the metric and dimension.
- Avoid colour-only meaning; cancellation should also be labelled explicitly.
- Provide alt text for visuals before publication.
- Keep font sizes readable at 100% zoom.
- Use thousands/millions display units consistently.
- Do not overload tooltips with raw technical keys.
- Test keyboard navigation and page order before final publication.

## Acceptance checklist

A report is not portfolio-ready until:

- all five pages are complete;
- every headline number reconciles to `docs/verified_results.md` with no slicers;
- AOV uses net sales / sale orders;
- customer pages carry the identity-coverage disclosure;
- no unsupported profit/margin metrics appear;
- screenshots are captured from the refreshed report, not mock-ups;
- the PBIP/PBIR source is committed after Power BI Desktop successfully reopens it.
