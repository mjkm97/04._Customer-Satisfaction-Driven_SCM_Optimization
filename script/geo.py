import pandas as pd
import numpy as np
import unicodedata
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

hash_map = {
    'SP': '남동부', 'RJ': '남동부', 'MG': '남동부',
    'RS': '남부', 'PR': '남부', 'SC': '남부',
    'BA': '북동부', 'DF': '중서부', 'ES': '남동부',
    'GO': '중서부', 'PE': '북동부', 'CE': '북동부',
    'PA': '북부', 'MT': '중서부', 'MA': '북동부',
    'MS': '중서부', 'PB': '북동부', 'PI': '북동부',
    'RN': '북동부', 'AL': '북동부', 'SE': '북동부',
    'TO': '북부', 'RO': '북부', 'AM': '북부',
    'AC': '북부', 'AP': '북부', 'RR': '북부'
}

geo = pd.read_csv('/app/spark/Olist/raw_data/olist_geolocation_dataset.csv')
# 다이어크리틱 문자 치환
def remove_diacritics(input_str):
    return ''.join(c for c in unicodedata.normalize('NFKD', input_str) if not unicodedata.combining(c))

geo['geolocation_city'] = geo['geolocation_city'].apply(remove_diacritics)

# Isolation Forest 
X = geo[['geolocation_lat', 'geolocation_lng']]

model = joblib.load('/app/spark/Olist/model/isolation_forest.pkl')
geo['anomaly_score'] = model.predict(X)

normal_geo = geo.loc[geo['anomaly_score']!=-1].copy()

le = LabelEncoder()
normal_geo['geo_encoded'] = le.fit_transform(normal_geo['geolocation_state'])
X,y= normal_geo[['geolocation_lat','geolocation_lng']].copy() ,normal_geo['geo_encoded'].copy()
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=42,stratify=y)

rf = joblib.load('/app/spark/Olist/model/rf.pkl')
outliers = geo.loc[geo['anomaly_score']==-1].copy()
X = outliers[['geolocation_lat','geolocation_lng']]
y_pred = rf.predict(X)

outliers['geolocation_state'] = le.inverse_transform(y_pred).tolist()

cleaned_geo = pd.concat([normal_geo, outliers], axis=0).reset_index(drop=True)
cleaned_geo.drop(['geo_encoded','anomaly_score'],axis=1,inplace=True)
cleaned_geo['geolocation_region']= cleaned_geo['geolocation_state'].map(hash_map)
cleaned_geo.to_csv('/app/spark/Olist/dim_table/dim_geo.csv',index=False)
print('geoloaction 전처리 완료')