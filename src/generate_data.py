from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

COUNTRIES = ["US", "CA", "GB", "DE", "AU"]
SEGMENTS = ["SMB", "Mid-market", "Enterprise"]
DEVICES = ["Mobile", "Desktop"]
METHODS = ["Card", "Wallet", "Bank debit", "BNPL"]
DECLINE_REASONS = ["issuer_decline", "insufficient_funds", "suspected_fraud", "expired_card", "network_error"]


def generate_payments(n: int = 300_000, seed: int = 42) -> pd.DataFrame:
    """Generate a deterministic synthetic payments event table.

    The data deliberately contains one interpretable performance deterioration:
    from June 2026 onward, card payments from SMB merchants on mobile devices in
    Canada and Great Britain experience an elevated issuer-decline rate.
    """
    rng = np.random.default_rng(seed)

    dates = pd.date_range("2026-01-01", "2026-08-31 23:59:59", freq="min")
    ts = rng.choice(dates.values, size=n, replace=True)
    ts = pd.to_datetime(ts)

    country = rng.choice(COUNTRIES, size=n, p=[0.46, 0.16, 0.14, 0.12, 0.12])
    segment = rng.choice(SEGMENTS, size=n, p=[0.56, 0.30, 0.14])
    device = rng.choice(DEVICES, size=n, p=[0.64, 0.36])
    method = rng.choice(METHODS, size=n, p=[0.63, 0.20, 0.11, 0.06])

    merchant_id = np.array([f"m_{x:05d}" for x in rng.integers(1, 5001, size=n)])
    customer_id = np.array([f"c_{x:07d}" for x in rng.integers(1, 180_001, size=n)])

    base_amount = rng.lognormal(mean=3.5, sigma=0.9, size=n)
    multipliers = np.where(segment == "Enterprise", 2.2, np.where(segment == "Mid-market", 1.45, 1.0))
    amount = np.round(np.clip(base_amount * multipliers, 3, 5000), 2)

    # Baseline success probability varies by method and device.
    p_success = np.full(n, 0.943)
    p_success += np.where(method == "Wallet", 0.014, 0)
    p_success += np.where(method == "Bank debit", -0.012, 0)
    p_success += np.where(method == "BNPL", -0.022, 0)
    p_success += np.where(device == "Mobile", -0.006, 0)
    p_success += np.where(country == "DE", -0.004, 0)

    incident = (
        (ts >= pd.Timestamp("2026-06-01"))
        & np.isin(country, ["CA", "GB"])
        & (segment == "SMB")
        & (device == "Mobile")
        & (method == "Card")
    )
    p_success -= np.where(incident, 0.082, 0)
    p_success = np.clip(p_success, 0.75, 0.985)

    success = rng.random(n) < p_success

    decline_reason = np.full(n, "", dtype=object)
    failures = ~success
    # During the incident, failures are disproportionately issuer declines.
    for mask, probs in [
        (failures & incident, [0.66, 0.13, 0.08, 0.06, 0.07]),
        (failures & ~incident, [0.31, 0.26, 0.17, 0.14, 0.12]),
    ]:
        idx = np.where(mask)[0]
        if len(idx):
            decline_reason[idx] = rng.choice(DECLINE_REASONS, size=len(idx), p=probs)

    refund = success & (rng.random(n) < np.where(method == "BNPL", 0.025, 0.016))
    dispute = success & (rng.random(n) < np.where(method == "Card", 0.0065, 0.0025))
    latency_ms = np.maximum(100, rng.normal(720, 210, size=n) + np.where(method == "Bank debit", 310, 0)).astype(int)

    # Fictional platform revenue assumption: 1.9% of successful gross payment volume.
    successful_amount = np.where(success, amount, 0.0)
    revenue = np.round(successful_amount * 0.019, 2)

    df = pd.DataFrame(
        {
            "payment_id": [f"pay_{i:09d}" for i in range(1, n + 1)],
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "event_ts": ts,
            "country": country,
            "merchant_segment": segment,
            "device": device,
            "payment_method": method,
            "amount_usd": amount,
            "payment_succeeded": success.astype(int),
            "decline_reason": decline_reason,
            "refund_flag": refund.astype(int),
            "dispute_flag": dispute.astype(int),
            "processing_latency_ms": latency_ms,
            "platform_revenue_usd": revenue,
        }
    )
    return df.sort_values("event_ts").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=300_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/payments.csv"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = generate_payments(args.rows, args.seed)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df):,} synthetic payment events to {args.output}")


if __name__ == "__main__":
    main()
