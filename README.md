# Payments Intelligence

**End-to-end payments analytics case study built on 1,000,000 deterministic synthetic payment events.**

[**Live portfolio site**](https://IamGRootMSE.github.io/-payments-intelligence/) · [Decision memo](https://IamGRootMSE.github.io/-payments-intelligence/decision-memo.html) · [Architecture](docs/architecture.md) · [Data dictionary](docs/data_dictionary.md)

> **Data classification:** 100% synthetic. No customer, employer, or proprietary data is used.

## What this project demonstrates

This repository is designed as a recruiter-reviewable analytics product rather than a notebook dump. It shows how I structure a business problem from raw events through a reusable metric layer to a decision recommendation.

- **Python data pipeline** generating 1M deterministic payment events
- **SQL analytics models** for staging, intermediate, and mart layers
- **Canonical KPI definitions** for payment success, successful volume, refunds, disputes, and platform revenue
- **PySpark implementation pattern** for distributed monthly aggregation
- **Automated data-quality tests** with `pytest`
- **GitHub Actions quality gate** on push and pull request
- **Interactive executive dashboard** published as a static recruiter-facing site
- **Root-cause diagnosis** with quantified business impact
- **Executive decision memo** separating evidence from the next operational validation step

## Business problem

A fictional payments platform sees payment performance soften. Leadership needs to know:

1. Where is success deteriorating?
2. Which merchant and customer contexts are affected?
3. What failure mode is driving the change?
4. What is the recoverable payment-volume opportunity?
5. What should Product / Payments Operations investigate first?

The synthetic generator deliberately injects one interpretable incident from June 2026 onward: **mobile card payments from SMB merchants in Canada and Great Britain experience elevated issuer declines**.

With the default seed, the affected cohort moves from approximately **93.7% to 85.9% payment success**, a deterioration of roughly **782 basis points**. Issuer declines increase from about **29.5% to 65.1% of failed attempts** in that cohort.

The point is not the fictional number. The point is that the entire finding is reproducible from code.

## System design

```text
Synthetic event generator
        |
        v
Raw payment attempts (1 row / attempt)
        |
        +------------------+
        |                  |
        v                  v
Python reference      SQL warehouse models
pipeline                   |
        |                  |
        +---------+--------+
                  v
          Canonical metric layer
                  |
          +-------+--------+
          |                |
          v                v
     QA / tests       Executive site
                           |
                           v
                  Diagnosis + decision
```

An optional PySpark path mirrors the canonical monthly aggregation for distributed environments.

## Repository structure

```text
payments-intelligence/
├── src/
│   ├── generate_data.py      # deterministic event generator
│   ├── metrics.py            # canonical metric calculations
│   ├── pipeline.py           # build sample + dashboard datasets
│   └── spark_pipeline.py     # optional PySpark path
├── sql/
│   ├── staging/
│   ├── intermediate/
│   └── marts/
├── tests/
│   └── test_metrics.py       # reconciliation + incident detection
├── data/sample/              # small reviewable extracts only
├── docs/
│   ├── index.html            # live dashboard / portfolio site
│   ├── app.js
│   ├── styles.css
│   ├── decision-memo.html
│   ├── architecture.md
│   └── data_dictionary.md
└── .github/workflows/
    ├── tests.yml             # CI quality gate
    └── pages.yml             # optional Pages deployment
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/pipeline.py
python -m pytest -q
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. The committed `docs/data.json` lets you preview the site without rebuilding. Use HTTP rather than opening the HTML file directly so the browser can load the JSON.

See [deployment instructions](DEPLOY.md) for GitHub Pages and Vercel.

## Rebuild with a different scale or seed

The generator can produce a larger or smaller event table independently:

```bash
python src/generate_data.py --rows 1500000 --seed 7 --output data/payments.csv
```

The published case study uses a fixed seed so a reviewer can reproduce the narrative.

## Metric contract

| Metric | Definition |
|---|---|
| Payment success rate | successful attempts / total attempts |
| Successful payment volume | amount on successful attempts |
| Refund rate | refunded successful attempts / successful attempts |
| Dispute rate | disputed successful attempts / successful attempts |
| Platform revenue | fictional 1.9% of successful payment volume |

See the full [data dictionary](docs/data_dictionary.md).

## Analytical conclusion

The evidence narrows the deterioration to a specific cohort and shows that the failure mix shifts sharply toward issuer declines. The recommendation is therefore **not** “redesign checkout everywhere.” It is to validate routing and issuer behavior in the affected cohort, then test targeted remediation while monitoring success rate, successful volume, refunds, and disputes as guardrails.

That distinction matters: analytics should reduce the decision space before it starts inventing causes.

## Author

**Prashanth Rajagopal**  
Analytics leader building decision systems across data engineering, statistics, business strategy, automation, and machine learning.

GitHub: [IamGRootMSE](https://github.com/IamGRootMSE)
