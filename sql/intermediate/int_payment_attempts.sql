-- Reusable metric-ready row grain: one record per payment attempt.

select
    payment_id,
    merchant_id,
    customer_id,
    event_ts,
    date_trunc('month', event_ts) as month,
    country,
    merchant_segment,
    device,
    payment_method,
    amount_usd,
    payment_succeeded,
    case when payment_succeeded = 1 then amount_usd else 0 end as successful_amount_usd,
    decline_reason,
    refund_flag,
    dispute_flag,
    processing_latency_ms,
    platform_revenue_usd
from stg_payments;
