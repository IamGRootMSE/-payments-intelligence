-- Canonical staging model for raw synthetic payment events.
-- Dialect: ANSI-ish SQL; tested conceptually against Databricks/Spark SQL conventions.

select
    cast(payment_id as string) as payment_id,
    cast(merchant_id as string) as merchant_id,
    cast(customer_id as string) as customer_id,
    cast(event_ts as timestamp) as event_ts,
    upper(country) as country,
    merchant_segment,
    device,
    payment_method,
    cast(amount_usd as decimal(18,2)) as amount_usd,
    cast(payment_succeeded as int) as payment_succeeded,
    nullif(decline_reason, '') as decline_reason,
    cast(refund_flag as int) as refund_flag,
    cast(dispute_flag as int) as dispute_flag,
    cast(processing_latency_ms as int) as processing_latency_ms,
    cast(platform_revenue_usd as decimal(18,2)) as platform_revenue_usd
from raw_payments
where payment_id is not null
  and event_ts is not null
  and amount_usd > 0;
