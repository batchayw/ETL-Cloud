from pyspark.sql import SparkSession # type: ignore
from pyspark.sql.functions import col, when, regexp_replace, to_timestamp, lit # type: ignore
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType # type: ignore

def main():
    spark = SparkSession.builder \
        .appName("ETL-DataCleaning") \
        .config("spark.hadoop.fs.s3a.access.key", "AKIAIOSFODNN7EXAMPLE") \
        .config("spark.hadoop.fs.s3a.secret.key", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    # Define schema for incoming data
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("email", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("created_at", TimestampType(), True),
        StructField("updated_at", TimestampType(), True),
        StructField("status", StringType(), True),
        StructField("value", DoubleType(), True)
    ])

    # Read raw data from MinIO
    raw_df = spark.read \
        .schema(schema) \
        .parquet("s3a://raw-data/*.parquet")

    # Data cleaning transformations
    cleaned_df = raw_df \
        .withColumn(
            "email",
            when(
                col("email").rlike("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"),
                col("email")
            ).otherwise(lit(None))
        ) \
        .withColumn(
            "phone",
            regexp_replace(col("phone"), "[^0-9]", "")
        ) \
        .withColumn(
            "status",
            when(col("status").isin(["active", "inactive", "pending"]), col("status"))
              .otherwise(lit("unknown"))
        ) \
        .na.drop(subset=["id"]) \
        .dropDuplicates(["id"])

    # Write cleaned data back to MinIO
    cleaned_df.write \
        .mode("overwrite") \
        .parquet("s3a://cleaned-data/")

    spark.stop()

if __name__ == "__main__":
    main()