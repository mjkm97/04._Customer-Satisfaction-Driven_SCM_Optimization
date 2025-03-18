'''
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, to_date, avg
import pandas as pd

# Spark 세션 생성
spark = SparkSession.builder.appName("Preproc").getOrCreate()
orders = spark.read.csv('/app/spark/Olist/raw_data/olist_order_items_dataset.csv',header=True, inferSchema=True)
orders.createOrReplaceTempView("orders_view")
# 중복 처리의 기준이 되는 열 조합
subset = ["order_id",'shipping_limit_date','seller_id','product_id']
query = """
    SELECT *
    FROM (
            SELECT * , ROW_NUMBER(order_item_id) OVER(ORDER BY )
                FROM orders_view
                GROUP BY order_id, shipping_limit_date , seller_id , product_id
    )

"""
'''

import pandas as pd
import numpy as np
orders = pd.read_csv("/app/spark/Olist/raw_data/olist_order_items_dataset.csv")
orders.head()
# 중복 처리의 기준이 되는 열 조합
subset = ["order_id",'shipping_limit_date','seller_id','product_id']
most_frequent_order_item = orders.groupby(subset)['order_item_id'].agg(lambda x: x.value_counts().idxmax())
orders['order_item_id'] = orders.groupby(subset)['order_item_id'].transform(
            lambda x: most_frequent_order_item.loc[x.name] if x.name in most_frequent_order_item else x)

# 첫번쨰 행만 남기고 중복된 행은 모두 제거
orders.drop_duplicates(subset=subset,keep='first',inplace=True)
orders.drop('order_item_id',axis=1,inplace=True)
orders.to_csv('/app/spark/Olist/fact_table/fact_itemz.csv',index=False)
print('item 테이블 전처리 완료')