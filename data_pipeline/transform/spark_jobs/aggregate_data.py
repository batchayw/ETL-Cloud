from pyspark.sql import SparkSession # type: ignore
from pyspark.sql.functions import col, sum, avg, count, date_format # type: ignore
from pyspark.sql.window import Window # type: ignore

def main():
    spark = SparkSession.builder \
        .appName("ETL-DataAggregation") \
        .config("spark.hadoop.fs.s3a.access.key", "AKIAIOSFODNN7EXAMPLE") \
        .config("spark.hadoop.fs.s3a.secret.key", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .getOrCreate()

    # Read enriched data
    enriched_df = spark.read.parquet("s3a://enriched-data/*.parquet")

    # Daily aggregations
    daily_metrics = enriched_df.groupBy(
        date_format(col("created_at"), "yyyy-MM-dd").alias("metric_date"),
        "customer_segment",
        "tier_name"
    ).agg(
        count("*").alias("customer_count"),
        sum("discounted_value").alias("total_value"),
        avg("discount").alias("avg_discount")
    )

    # Rolling 7-day metrics
    window_spec = Window.partitionBy("customer_segment", "tier_name") \
                       .orderBy("metric_date") \
                       .rowsBetween(-6, 0)

    rolling_metrics = daily_metrics.withColumn(
        "rolling_7d_value",
        sum("total_value").over(window_spec)
    ).withColumn(
        "rolling_7d_avg_discount",
        avg("avg_discount").over(window_spec)
    )

    # Write aggregated data
    rolling_metrics.write \
        .mode("overwrite") \
        .parquet("s3a://aggregated-data/")

    spark.stop()

if __name__ == "__main__":
    main()