from __future__ import annotations

import pandas as pd


def payment_metrics(df: pd.DataFrame) -> dict[str, float]:
    attempts = len(df)
    successes = int(df["payment_succeeded"].sum())
    attempted_volume = float(df["amount_usd"].sum())
    successful_volume = float((df["amount_usd"] * df["payment_succeeded"]).sum())
    refunds = int(df["refund_flag"].sum())
    disputes = int(df["dispute_flag"].sum())
    revenue = float(df["platform_revenue_usd"].sum())

    return {
        "attempts": attempts,
        "successes": successes,
        "success_rate": successes / attempts if attempts else 0.0,
        "attempted_volume_usd": attempted_volume,
        "successful_volume_usd": successful_volume,
        "refund_rate": refunds / successes if successes else 0.0,
        "dispute_rate": disputes / successes if successes else 0.0,
        "platform_revenue_usd": revenue,
    }


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["month"] = pd.to_datetime(x["event_ts"]).dt.to_period("M").astype(str)
    dims = ["month", "country", "merchant_segment", "device", "payment_method"]
    out = (
        x.groupby(dims, observed=True)
        .agg(
            attempts=("payment_id", "size"),
            successes=("payment_succeeded", "sum"),
            attempted_volume_usd=("amount_usd", "sum"),
            successful_volume_usd=("amount_usd", lambda s: 0.0),
            refunds=("refund_flag", "sum"),
            disputes=("dispute_flag", "sum"),
            platform_revenue_usd=("platform_revenue_usd", "sum"),
        )
        .reset_index()
    )
    # successful volume needs payment success mask at row-level; compute separately.
    x["successful_amount_usd"] = x["amount_usd"] * x["payment_succeeded"]
    sv = x.groupby(dims, observed=True)["successful_amount_usd"].sum().reset_index()
    out = out.drop(columns="successful_volume_usd").merge(sv, on=dims, how="left")
    out["success_rate"] = out["successes"] / out["attempts"]
    out["refund_rate"] = out["refunds"] / out["successes"].clip(lower=1)
    out["dispute_rate"] = out["disputes"] / out["successes"].clip(lower=1)
    return out
