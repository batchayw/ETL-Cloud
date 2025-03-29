from pyspark.sql import SparkSession # type: ignore
from pyspark.sql.functions import col, lit, when, concat # type: ignore
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType # type: ignore

def main():
    spark = SparkSession.builder \
        .appName("ETL-DataEnrichment") \
        .config("spark.hadoop.fs.s3a.access.key", "AKIAIOSFODNN7EXAMPLE") \
        .config("spark.hadoop.fs.s3a.secret.key", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .getOrCreate()

    # Read cleaned data
    cleaned_df = spark.read.parquet("s3a://cleaned-data/*.parquet")

    # Reference data (could be loaded from another source)
    ref_data = [
        (1, "premium", 0.2),
        (2, "standard", 0.1),
        (3, "basic", 0.0)
    ]
    ref_schema = StructType([
        StructField("tier_id", IntegerType()),
        StructField("tier_name", StringType()),
        StructField("discount", DoubleType())
    ])
    ref_df = spark.createDataFrame(ref_data, ref_schema)

    # Enrichment transformations
    enriched_df = cleaned_df \
        .join(ref_df, cleaned_df.id % 3 + 1 == ref_df.tier_id, "left") \
        .withColumn("discounted_value", col("value") * (1 - col("discount"))) \
        .withColumn("customer_segment", 
                   when(col("value") > 1000, "high_value")
                   .when(col("value") > 500, "medium_value")
                   .otherwise("low_value")) \
        .withColumn("full_name", concat(col("name"), lit(" (ID: "), col("id"), lit(")")))

    # Write enriched data
    enriched_df.write \
        .mode("overwrite") \
        .parquet("s3a://enriched-data/")

    spark.stop()

if __name__ == "__main__":
    main()