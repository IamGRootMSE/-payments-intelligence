# Architecture

```text
Synthetic event generator
        |
        v
Raw payment attempts
        |
        +--> staging SQL --------------+
        |                              |
        v                              v
Python reference pipeline       PySpark optional path
        |                              |
        +------------+-----------------+
                     v
             Canonical metric layer
                     |
        +------------+-------------+
        |                          |
        v                          v
Automated QA / tests       Recruiter-facing site
                                   |
                                   v
                     Executive diagnosis + decision
```

## Design principles

1. **Row grain is explicit.** Raw and intermediate models remain one row per payment attempt.
2. **Metrics reconcile.** Success, refund, dispute, and volume calculations share one canonical definition.
3. **Synthetic is stated everywhere.** This is a portfolio case study, not production customer data.
4. **The dashboard is decision-oriented.** The default view moves from health to diagnosis to action.
5. **The project is lightweight to review.** The public site is static and fast, while code remains inspectable.

## Data flow

`generate_data.py` produces deterministic payment events with a known injected deterioration. `pipeline.py` builds sample data and the aggregated JSON used by the site. SQL models demonstrate how the same logic would be represented in an analytics warehouse. `spark_pipeline.py` mirrors the monthly aggregation in PySpark for distributed environments.
