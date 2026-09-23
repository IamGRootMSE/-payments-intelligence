-- Daily fact table for monitoring and anomaly investigation.

select
    cast(event_ts as date) as payment_date,
    country,
    merchant_segment,
    device,
    payment_method,
    count(*) as attempts,
    sum(payment_succeeded) as successes,
    sum(amount_usd) as attempted_volume_usd,
    sum(successful_amount_usd) as successful_volume_usd,
    sum(refund_flag) as refunds,
    sum(dispute_flag) as disputes,
    sum(platform_revenue_usd) as platform_revenue_usd,
    avg(processing_latency_ms) as avg_processing_latency_ms
from int_payment_attempts
group by 1,2,3,4,5;
