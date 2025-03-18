''''
import pandas as pd
import numpy as np

# 데이터 읽기
orders = pd.read_csv("/app/spark/Olist/raw_data/olist_orders_dataset.csv")

# order_approved_at 결측치는 order_purchase_timestamp로 대체
orders['order_approved_at'] = orders['order_approved_at'].fillna(orders['order_purchase_timestamp'])

# days_to_delivery, estimated_days_to_delivery 컬럼 생성
orders['days_to_delivery'] = (pd.to_datetime(orders['order_delivered_customer_date']) - pd.to_datetime(orders['order_approved_at'])).dt.days
orders['estimated_days_to_delivery'] = (pd.to_datetime(orders['order_estimated_delivery_date']) - pd.to_datetime(orders['order_approved_at'])).dt.days

# timestamp 컬럼을 날짜 형식으로 변환
date_cols = ['order_delivered_carrier_date', 'order_delivered_customer_date', 'order_purchase_timestamp', 'order_estimated_delivery_date', 'order_approved_at']
orders[date_cols] = orders[date_cols].apply(pd.to_datetime).apply(lambda x: x.dt.strftime('%Y-%m-%d'))

# 음수값 날리기
orders = orders[(orders['days_to_delivery'] >= 0) & (orders['estimated_days_to_delivery'] >= 0)]

# 이상치 처리
q1_days, q3_days = np.percentile(orders['days_to_delivery'], [25, 75])
iqr_days = q3_days - q1_days
orders = orders[(orders['days_to_delivery'] >= q1_days - 1.5 * iqr_days) & (orders['days_to_delivery'] <= q3_days + 1.5 * iqr_days)]

q1_estimated, q3_estimated = np.percentile(orders['estimated_days_to_delivery'], [25, 75])
iqr_estimated = q3_estimated - q1_estimated
orders = orders[(orders['estimated_days_to_delivery'] >= q1_estimated - 1.5 * iqr_estimated) & (orders['estimated_days_to_delivery'] <= q3_estimated + 1.5 * iqr_estimated)]

# 평균 배송 일수 계산
avg_delivery = orders['days_to_delivery'].mean()

# 지연 플래그 추가
orders['delay_flag_estimated'] = np.where(orders['days_to_delivery'] > orders['estimated_days_to_delivery'], 1, 0)
orders['delay_flag_avg'] = np.where(orders['days_to_delivery'] > avg_delivery, 1, 0)

# 결과를 CSV 파일로 저장
orders.to_csv('/app/spark/Olist/fact_table/fact_orders.csv', index=False)
print('Order 테이블 전처리 완료')
'''
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, to_date, avg
import pandas as pd

# Spark 세션 생성
spark = SparkSession.builder.appName("Preproc").getOrCreate()

orders = spark.read.csv("/app/spark/Olist/raw_data/olist_orders_dataset.csv", header=True, inferSchema=True)

# order_approved_at 결측치는 order_purchase_timestamp로 대체
orders = orders.withColumn("order_approved_at", expr("CASE WHEN order_approved_at IS NULL THEN order_purchase_timestamp ELSE order_approved_at END")) \
                .withColumn("days_to_delivery", expr("DATEDIFF(order_delivered_customer_date, order_approved_at)")) \
                .withColumn("estimated_days_to_delivery", expr("DATEDIFF(order_estimated_delivery_date, order_approved_at)")) \
                .withColumn("order_delivered_carrier_date", to_date(col("order_delivered_carrier_date"))) \
                .withColumn("order_delivered_customer_date", to_date(col("order_delivered_customer_date"))) \
                .withColumn("order_purchase_timestamp", to_date(col("order_purchase_timestamp"))) \
                .withColumn("order_estimated_delivery_date", to_date(col("order_estimated_delivery_date"))) \
                .withColumn("order_approved_at", to_date(col("order_approved_at")))

# 음수값 날리기
orders = orders.filter("days_to_delivery >= 0 AND estimated_days_to_delivery >= 0")

# 이상치 처리
q1, q3 = orders.approxQuantile("days_to_delivery", [0.25, 0.75], 0.05)
iqr = q3 - q1
orders = orders.filter((col("days_to_delivery") >= q1 - 1.5 * iqr) & (col("days_to_delivery") <= q3 + 1.5 * iqr))

q1, q3 = orders.approxQuantile("estimated_days_to_delivery", [0.25, 0.75], 0.05)
iqr = q3 - q1
orders = orders.filter((col("estimated_days_to_delivery") >= q1 - 1.5 * iqr) & (col("estimated_days_to_delivery") <= q3 + 1.5 * iqr))

# 평균 배송 일수 계산
avg_delivery = orders.select(avg('days_to_delivery')).collect()[0][0]

# 지연 플래그 추가
orders = orders.withColumn("delay_flag_estimated", expr("CASE WHEN days_to_delivery > estimated_days_to_delivery THEN 1 ELSE 0 END")) \
                .withColumn("delay_flag_avg", expr(f"CASE WHEN days_to_delivery > {avg_delivery} THEN 1 ELSE 0 END"))

# 결과를 CSV 파일로 저장
orders.toPandas().to_csv('/app/spark/Olist/fact_table/fact_orders.csv', index=False)
print('Oder 테이블 전처리 완료')
spark.stop()