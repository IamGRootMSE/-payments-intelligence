import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from generate_data import generate_payments
from metrics import aggregate_monthly, payment_metrics


def test_generation_is_deterministic():
    a = generate_payments(1000, 7)
    b = generate_payments(1000, 7)
    pd.testing.assert_frame_equal(a, b)


def test_metric_rates_are_bounded():
    df = generate_payments(5000, 12)
    m = payment_metrics(df)
    assert 0 <= m["success_rate"] <= 1
    assert 0 <= m["refund_rate"] <= 1
    assert 0 <= m["dispute_rate"] <= 1


def test_monthly_attempts_reconcile():
    df = generate_payments(5000, 21)
    agg = aggregate_monthly(df)
    assert int(agg["attempts"].sum()) == len(df)
    assert int(agg["successes"].sum()) == int(df["payment_succeeded"].sum())


def test_injected_incident_is_detectable():
    df = generate_payments(120_000, 42)
    focus = df[
        df["country"].isin(["CA", "GB"])
        & (df["merchant_segment"] == "SMB")
        & (df["device"] == "Mobile")
        & (df["payment_method"] == "Card")
    ]
    before = focus[pd.to_datetime(focus["event_ts"]) < pd.Timestamp("2026-06-01")]["payment_succeeded"].mean()
    after = focus[pd.to_datetime(focus["event_ts"]) >= pd.Timestamp("2026-06-01")]["payment_succeeded"].mean()
    assert before - after > 0.04
