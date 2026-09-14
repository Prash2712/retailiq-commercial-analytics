# DAX measure catalogue

The TMDL model implements these measures. This document exists to make the metric contract easy to review without reading the full model script.

## Commercial measures

### Gross Sales Value

```DAX
Gross Sales Value =
CALCULATE(
    SUM('Fact Transactions'[Line Value]),
    'Fact Transactions'[Event Type] = "sale"
)
```

Expected full-source value: **£20,972,594.5680**.

### Cancellation Value

```DAX
Cancellation Value =
CALCULATE(
    SUMX('Fact Transactions', ABS('Fact Transactions'[Line Value])),
    'Fact Transactions'[Event Type] = "cancellation"
)
```

Expected full-source value: **£1,527,415.0000**.

### Net Sales Value

```DAX
Net Sales Value = [Gross Sales Value] - [Cancellation Value]
```

Expected full-source value: **£19,445,179.5680**.

### Sale Orders

```DAX
Sale Orders =
CALCULATE(
    DISTINCTCOUNT('Fact Transactions'[Invoice No]),
    'Fact Transactions'[Event Type] = "sale"
)
```

Expected full-source value: **40,077**.

### Cancellation Orders

```DAX
Cancellation Orders =
CALCULATE(
    DISTINCTCOUNT('Fact Transactions'[Invoice No]),
    'Fact Transactions'[Event Type] = "cancellation"
)
```

Expected full-source value: **11,685** cancellation-order events.

### Average Order Value

```DAX
Average Order Value = DIVIDE([Net Sales Value], [Sale Orders])
```

The project uses **net sales / sale orders** as the governed AOV definition. Expected full-source value is approximately **£485.20**.

### Units Sold

```DAX
Units Sold =
CALCULATE(
    SUM('Fact Transactions'[Quantity]),
    'Fact Transactions'[Event Type] = "sale"
)
```

### Known Customers

```DAX
Known Customers =
CALCULATE(
    DISTINCTCOUNT('Fact Transactions'[Customer Key]),
    'Fact Transactions'[Event Type] = "sale",
    'Fact Transactions'[Customer Key] <> BLANK()
)
```

Expected full-source value: **5,878**.

### Cancellation Value %

```DAX
Cancellation Value % = DIVIDE([Cancellation Value], [Gross Sales Value])
```

Expected full-source value: approximately **7.28%**.

## Customer measures

### Repeat Customers

```DAX
Repeat Customers =
CALCULATE(
    COUNTROWS('Customer Summary'),
    'Customer Summary'[Is Repeat Customer] = TRUE()
)
```

Expected full-source value: **4,255**.

### Identifiable Purchasing Customers

```DAX
Identifiable Purchasing Customers = COUNTROWS('Customer Summary')
```

Expected full-source value: **5,878**.

### Repeat Customer Rate

```DAX
Repeat Customer Rate =
DIVIDE([Repeat Customers], [Identifiable Purchasing Customers])
```

Expected full-source value: **72.39%**.

## Time-intelligence measures

### Prior Year Net Sales

```DAX
Prior Year Net Sales =
CALCULATE(
    [Net Sales Value],
    DATEADD('Date'[Date], -1, YEAR)
)
```

### Net Sales YoY %

```DAX
Net Sales YoY % =
DIVIDE(
    [Net Sales Value] - [Prior Year Net Sales],
    [Prior Year Net Sales]
)
```

Use only where the selected period has a valid prior-year comparison. The source begins on 1 December 2009 and ends on 9 December 2011, so edge periods are incomplete.

### Net Sales YTD

```DAX
Net Sales YTD =
TOTALYTD([Net Sales Value], 'Date'[Date])
```

## Concentration measures

### Top 10 Product Net Sales

```DAX
Top 10 Product Net Sales =
SUMX(
    TOPN(
        10,
        ALLSELECTED('Product'[Stock Code]),
        [Net Sales Value],
        DESC
    ),
    [Net Sales Value]
)
```

### Top 10 Product Share

```DAX
Top 10 Product Share = DIVIDE([Top 10 Product Net Sales], [Net Sales Value])
```

## Data-quality measures

### Repeated Exact Rows

```DAX
Repeated Exact Rows =
CALCULATE(
    COUNTROWS('Fact Transactions'),
    'Fact Transactions'[Is Repeated Exact Row] = TRUE()
)
```

Expected full-source value: **34,335**.

### Missing Customer ID Rows

```DAX
Missing Customer ID Rows =
CALCULATE(
    MAX('Data Quality'[Value]),
    'Data Quality'[Metric] = "missing_customer_id"
)
```

Expected full-source value: **243,007**.

### Fact Row Count

```DAX
Fact Row Count = COUNTROWS('Fact Transactions')
```

Expected full-source value: **1,067,371**.

## Validation rules

1. Headline cards must use measures, never implicit column aggregation.
2. AOV must use **net sales / sale orders** consistently.
3. Product and geography visuals should inherit filter context from the star-schema dimensions.
4. Customer Summary, Customer RFM and Cohort Retention are helper marts with their own documented population basis.
5. Customer metrics must not be presented as covering anonymous transactions.
6. Any new measure added in Power BI must be documented here and mapped to either the fact model or a named SQL mart.
