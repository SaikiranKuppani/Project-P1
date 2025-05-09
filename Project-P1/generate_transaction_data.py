from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder \
    .appName("CleanAndWriteFailedTransactions") \
    .getOrCreate()

# Read all CSV files into one DataFrame
df = spark.read.csv("gs://sai-bucket12/BankTransactions/*.csv", header=True, inferSchema=True)


# Drop rows where any column is null or blank
df_cleaned = df.na.drop()
df_cleaned = df_cleaned.filter(
    (col("transaction_id") != "") &
    (col("account_no") != "") &
    (col("amount").isNotNull())
)

# Filter for failed transactions only
df_failed = df_cleaned.filter(col("status") == "Failed")

# MySQL connection properties
jdbc_url = "jdbc:mysql://35.194.20.53:3306/Bank"
properties = {
    "user": "mark",
    "password": "12345",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# Write the failed transactions to MySQL
df_failed.write.jdbc(url=jdbc_url, table="failed_transactions", mode="overwrite", properties=properties)

# Stop Spark session
spark.stop()
