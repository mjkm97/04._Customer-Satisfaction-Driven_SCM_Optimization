from pyspark.sql import SparkSession
# Spark 세션 생성
spark = (
    SparkSession.builder
    .appName("olist")
    .config("spark.driver.memory", "6g")
    .config("spark.executor.memory", "6g")
    .config("spark.sql.shuffle.partitions", "8")
    .getOrCreate()
)

orders = spark.read.csv('/app/spark/Olist/fact_table/fact_orders.csv')
items=spark.read.csv('/app/spark/Olist/fact_table/fact_items.csv')
order_items = orders.join(items, on='order_id')

