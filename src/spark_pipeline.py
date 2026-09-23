"""Optional PySpark implementation of the canonical monthly metric layer.

This module mirrors the pandas reference pipeline for teams that run Spark.
It is intentionally isolated so the core demo remains lightweight to run.
"""


def build_monthly_metrics_spark(spark, input_path: str, output_path: str) -> None:
    from pyspark.sql import functions as F

    df = spark.read.option("header", True).option("inferSchema", True).csv(input_path)
    enriched = (
        df.withColumn("event_ts", F.to_timestamp("event_ts"))
        .withColumn("month", F.date_format("event_ts", "yyyy-MM"))
        .withColumn("successful_amount_usd", F.col("amount_usd") * F.col("payment_succeeded"))
    )

    dims = ["month", "country", "merchant_segment", "device", "payment_method"]
    metrics = (
        enriched.groupBy(*dims)
        .agg(
            F.count("payment_id").alias("attempts"),
            F.sum("payment_succeeded").alias("successes"),
            F.sum("amount_usd").alias("attempted_volume_usd"),
            F.sum("successful_amount_usd").alias("successful_volume_usd"),
            F.sum("refund_flag").alias("refunds"),
            F.sum("dispute_flag").alias("disputes"),
            F.sum("platform_revenue_usd").alias("platform_revenue_usd"),
        )
        .withColumn("success_rate", F.col("successes") / F.col("attempts"))
        .withColumn("refund_rate", F.col("refunds") / F.greatest(F.col("successes"), F.lit(1)))
        .withColumn("dispute_rate", F.col("disputes") / F.greatest(F.col("successes"), F.lit(1)))
    )

    metrics.write.mode("overwrite").parquet(output_path)
