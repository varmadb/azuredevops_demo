# Databricks notebook source
container = "databrickscontainer"
storage = "varmadbsa"
sas = "sp=racwdl&st=2021-09-11T16:25:30Z&se=2021-09-12T00:25:30Z&sv=2020-08-04&sr=c&sig=WZ0Kyu68S0p6QUNeAogCS%2B3sZoFiz8VkEeDN2wyGr0c%3D"

spark.conf.set(
  f"fs.azure.sas.{container}.{storage}.blob.core.windows.net",
  sas)
  

#productCounts.repartition(1).write.mode('overwrite').csv("wasb://databricks@dbdatabrickstest.blob.core.windows.net/output", header="true")

 


# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import *

# The log file name is a parameter passed to the job with a default value of IISlog.txt
filePath = "wasb://spark@<YOUR_ACCOUNT>.blob.core.windows.net/data/" + getArgument("logFile", "IISlog.txt")
filePath = "wasbs://databricks@dbdatabrickstest.blob.core.windows.net/" + getArgument("logFile", "IISlog.txt")
#filePath = "wasb://dbdatabrickstest.blob.core.windows.net/" + getArgument("logFile", "IISlog.txt")

# Define the schema of the log file
log_schema = StructType([
  StructField("date", TimestampType(), False),
  StructField("time", StringType(), False),
  StructField("c_ip", StringType(), False),
  StructField("cs_username", StringType(), False),
  StructField("s_ip", StringType(), False),
  StructField("s_port", IntegerType(), False),
  StructField("cs_method", StringType(), False),
  StructField("cs_uri_stem", StringType(), False),
  StructField("cs_uri_query", StringType(), False),
  StructField("sc_status", IntegerType(), False),
  StructField("sc_bytes", IntegerType(), False),
  StructField("cs_bytes", IntegerType(), False),
  StructField("time_taken", IntegerType(), False),
  StructField("cs_user_agent", StringType(), False),
  StructField("cs_referrer", StringType(), False)
])

# Read the space-delimited log file, ignoring commented lines that start with a # character
df = spark.read.csv(filePath, sep=" ", schema=log_schema, header="false", comment="#")

df.count

# COMMAND ----------

# Filter to include only product.aspx page views, and count the entries for each distinct query string (which includes the specific product ID viewed)
pageCounts = df.filter("cs_uri_stem = '/product.aspx'").select("cs_uri_query").groupby("cs_uri_query").count().orderBy(desc("count"))

# Rename the columns to products and hits
productCounts = pageCounts.select(col("cs_uri_query").alias("product"), col("count").alias("hits"))

productCounts.repartition(1).write.mode('overwrite').csv("wasbs://databricks@dbdatabrickstest.blob.core.windows.net/output", header="true")
# Combine the results to a single partition and write them out as a CSV file.
#productCounts.repartition(1).write.mode('overwrite').csv("wasb://spark@<YOUR_ACCOUNT>.blob.core.windows.net/output", header="true")
