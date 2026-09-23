# Data dictionary

| Field | Grain / type | Definition |
|---|---|---|
| `payment_id` | string | Unique synthetic payment attempt |
| `merchant_id` | string | Synthetic merchant identifier |
| `customer_id` | string | Synthetic customer identifier |
| `event_ts` | timestamp | Attempt timestamp |
| `country` | category | US, CA, GB, DE, AU |
| `merchant_segment` | category | SMB, Mid-market, Enterprise |
| `device` | category | Mobile or Desktop |
| `payment_method` | category | Card, Wallet, Bank debit, BNPL |
| `amount_usd` | currency | Attempted payment amount |
| `payment_succeeded` | binary | 1 if the payment succeeded |
| `decline_reason` | category | Populated for failed payments |
| `refund_flag` | binary | 1 if a successful payment was later refunded |
| `dispute_flag` | binary | 1 if a successful payment was disputed |
| `processing_latency_ms` | integer | Synthetic processing latency |
| `platform_revenue_usd` | currency | Fictional 1.9% fee on successful volume |

## Canonical metrics

**Success rate** = successful attempts / total attempts  
**Successful payment volume** = sum(amount) for successful attempts  
**Refund rate** = refunded successful attempts / successful attempts  
**Dispute rate** = disputed successful attempts / successful attempts  
**Platform revenue** = 1.9% of successful payment volume for this fictional case study
