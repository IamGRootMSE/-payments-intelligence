from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from generate_data import generate_payments
from metrics import aggregate_monthly, payment_metrics


def build(rows: int = 1_000_000, seed: int = 42, root: Path = Path(".")) -> None:
    df = generate_payments(rows, seed)

    sample_dir = root / "data" / "sample"
    web_dir = root / "docs"
    sample_dir.mkdir(parents=True, exist_ok=True)
    web_dir.mkdir(parents=True, exist_ok=True)

    df.head(5_000).to_csv(sample_dir / "payments_sample.csv", index=False)
    agg = aggregate_monthly(df)
    agg.to_csv(sample_dir / "monthly_metrics.csv", index=False)

    # Root-cause table for the deliberately injected incident.
    x = df.copy()
    x["period"] = pd.Series("baseline", index=x.index)
    x.loc[pd.to_datetime(x["event_ts"]) >= pd.Timestamp("2026-06-01"), "period"] = "incident"

    focus = x[
        x["country"].isin(["CA", "GB"])
        & (x["merchant_segment"] == "SMB")
        & (x["device"] == "Mobile")
        & (x["payment_method"] == "Card")
    ].copy()

    baseline = focus[focus["period"] == "baseline"]
    incident = focus[focus["period"] == "incident"]
    b = payment_metrics(baseline)
    i = payment_metrics(incident)

    issuer_share_baseline = (
        (baseline["decline_reason"] == "issuer_decline").sum() / max((baseline["payment_succeeded"] == 0).sum(), 1)
    )
    issuer_share_incident = (
        (incident["decline_reason"] == "issuer_decline").sum() / max((incident["payment_succeeded"] == 0).sum(), 1)
    )
    recovered_volume = max(0.0, i["attempted_volume_usd"] * (b["success_rate"] - i["success_rate"]))

    diagnosis = {
        "focus": "CA + GB | SMB | Mobile | Card",
        "baseline_success_rate": b["success_rate"],
        "incident_success_rate": i["success_rate"],
        "delta_bps": (i["success_rate"] - b["success_rate"]) * 10_000,
        "issuer_decline_share_baseline": issuer_share_baseline,
        "issuer_decline_share_incident": issuer_share_incident,
        "estimated_recoverable_successful_volume_usd": recovered_volume,
        "incident_attempts": i["attempts"],
    }

    payload = {
        "meta": {
            "synthetic": True,
            "rows_generated": rows,
            "seed": seed,
            "period": "2026-01-01 to 2026-08-31",
            "revenue_assumption": "1.9% of successful payment volume",
        },
        "overall": payment_metrics(df),
        "diagnosis": diagnosis,
        "monthly": json.loads(agg.round(6).to_json(orient="records")),
    }
    (web_dir / "data.json").write_text(json.dumps(payload, indent=2))

    print(json.dumps(diagnosis, indent=2))


if __name__ == "__main__":
    build()
