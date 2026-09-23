-- Canonical payment-health semantic layer used by the executive dashboard.

with base as (
    select
        month,
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
        sum(platform_revenue_usd) as platform_revenue_usd
    from int_payment_attempts
    group by 1,2,3,4,5
)
select
    *,
    successes / nullif(attempts, 0) as success_rate,
    refunds / nullif(successes, 0) as refund_rate,
    disputes / nullif(successes, 0) as dispute_rate
from base;
