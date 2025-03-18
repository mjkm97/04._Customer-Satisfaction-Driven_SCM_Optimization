from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, to_date, date_format, from_utc_timestamp
import pandas as pd

# Spark 세션 생성
spark = SparkSession.builder.appName("CreateDimDate").getOrCreate()

# 날짜 범위 생성 (2016년 1월 1일 ~ 2019년 1월 1일)
date_range = pd.date_range(start="2016-01-01", end="2019-01-01", freq='D')
date_df = pd.DataFrame({'full_date': date_range}) 

dim_date = spark.createDataFrame(date_df)

# 날짜 변환 America/Sao_Paulo 상파울루 시간대로 변환
dim_date = dim_date.withColumn("full_date", to_date(from_utc_timestamp(col("full_date"), "America/Sao_Paulo")))

dim_date = dim_date.withColumn("year",expr("YEAR(full_date)")) \
                   .withColumn("month",expr("MONTH(full_date)")) \
                   .withColumn("day",expr("DAY(full_date)")) \
                   .withColumn("week",expr("WEEKOFYEAR(full_date)")) \
                   .withColumn("quarter",expr("QUARTER(full_date)")) \
                   .withColumn("day_of_week", date_format(col("full_date"), "EEEE")) \
                   .withColumn("is_weekend", expr("CASE WHEN day_of_week IN ('Saturday', 'Sunday') THEN 1 ELSE 0 END"))
print(dim_date.show())

dim_date.toPandas().to_csv("/app/spark/Olist/dim_table/dim_date.csv", index=False)
print("dim_date.csv 파일 생성 완료")
spark.stop()