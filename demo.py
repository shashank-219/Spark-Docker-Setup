from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("LocalSparkDemo")
    .master("local[2]")
    .config("spark.sql.shuffle.partitions", "2")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

try:
    employees = (
        spark.read.option("header", True)
        .schema("name STRING, department STRING, salary INT")
        .csv("/workspace/employees.csv")
    )

    employees.groupBy("department").agg(
        F.count("*").alias("employee_count"),
        F.avg("salary").alias("average_salary"),
    ).orderBy("department").show()
finally:
    spark.stop()
