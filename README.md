# 프로젝트 04. 고객 만족 중심의 SCM 최적화

**- 소비자 만족 원인 배송지연 문제 해결을 위한 최적의 물류센터 위치 제안**   

### 프로젝트 주제: 소비자 만족도의 원인인 배송지연 문제 해결을 위한 최적의 **물류센터 위치 제안**

### **목차**

1. 서론: 프로젝트 배경 및 목표
2. 본론
    1. 리뷰데이터 분석을 통한 문제 설정  
    2. 머신러닝으로 소비자 만족도의 주요 원인 파악 및 검증
    3. 배송 시간 단축을 위한 물류센터의 위치 선정 및 제안 
3.  결론 및 전망

**사용한 툴**

- 전처리: 파이썬
- 분석: SQL, 파이썬
- 시각화: 태블로, 엑셀, 파이썬(시각화, ML)

**사용한 분석 기법**

- 리뷰 텍스트 빈도 분석 / TF-IDF (중요 단어 가중치 계산)
- 리뷰 텍스트 감성 분석
- ML(TabNet,Mlp,Rf,Boosting 모델..)을 활용한 회귀분석

# **1. 서론: 프로젝트 배경 및 목표**

<aside>
💡

프로젝트 개요 

- 리뷰 데이터 분석을 통해 배송 지연 여부와 소비자 만족도(리뷰 평점) 간 높은 상관관계를 발견함
- **분석 과제:** 배송 지연 감소를 위한 물류센터 배치 전략
- **분석 목적:** 물류센터의 위치를 최적화 하여 배송 지연을 줄이고자 한다
</aside>

**📌 Step 1. 문제 설정** 

- **배경 :** 리뷰점수 정량분석, 텍스트 정성분석을 통해 배송 지연 여부와 매출 및 소비자 만족도 간 높은 상관관계가 존재하는 것을 발견함
- 배송지연(예상배송일 보다 실제배송 완료일이 늦을 때)이 소비자 만족도의 주요 원인 중 하나
- 배송시간이 1.5일 단축되면, 고객만족 향상 (리뷰 점수 개선) , 2일 이상 지연될 경우 리뷰점수 하락

**📌Step 2.  머신러닝으로 소비자 만족도의 주요 원인 파악 및 검증**

- TabNet,RF,XGB,LGBM 변수중요도 분석을 통해 공통적으로 중요도가 높은 변수를 파악
    - carrier_to_customer (물류회사 → 고객에게 택배 배송 완료까지 걸린 시간)
    - customer_lat,lng(고객의 위경도 데이터)
- 이에 따라 소비자 만족을 위해 물류회사에서 고객에게 배송 완료까지 소요되는 시간을 단축시킬 수 있도록, 물류센터 위치 선정이 중요하다고 판단함
    
    

**📌Step 3. 문제 해결을 위한 제안 및 예상 효과**

- 배송지연 개선 및 배송기간 단축을 위한 최적의 물류센터 위치 선정
- 최적의 물류센터 위치로 선정한 곳으로 물류센터 신설 시, 배송일이 1.19일 단축 될 수 있음

### **가설**

1. **배송 소요 기간과 고객 리뷰 점수 분석:** 
    - 배송 소요 기간과 고객 리뷰 점수 간 연관이 있을 것이다.
2. 소비자 만족(리뷰 내용, 리뷰 점수)의 주요 원인은 배송지연이다. 
3. 물류센터 위치 최적화 시, 배송 지연 문제를 해결할 수 있다. 

### 가설 검증 방법

1. 배송 소요 기간과 고객 리뷰 점수 분석
    1. 리뷰 데이터 내 배송 관련 키워드(긍정/부정) 감성 분석
    2. 판매자 구매자 주에 따른 배송 소요 기간 분석
    3. 배송 지연과 리뷰 점수 분석[Tf-idf]
2. [RoBERTa]
    1. https://huggingface.co/citizenlab/twitter-xlm-roberta-base-sentiment-finetunned
3. ML (random forest, lightgbm), 통계분석(ANOVA) 통해 가설이 맞는 지 검증 

<aside>

### **A. 사용한 Raw 데이터 세트: Brazilian Olist**

- 링크: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
    
    ![image.png](project_readme_image/image.png)
    
- 특징:
    - 대부분의 고객이 단발성 구매 고객으로 나타나 RFM 분석에 적합하지 않음
    - 고객의 구매 여정 관련 로그 데이터가 존재하지 않아 퍼널 분석을 수행하는 데에 적합하지 않음

### B. 데이터 전처리

- **논리**: 분석에 적합하도록  garbage in garbage out 으로 전처리
- **전처리 데이터 포인트:**
    - [order_table](https://www.notion.so/1a1cd66266a0801c93dff6b2412dbead?pvs=21) :  배송기간 이상값 제거(`배송기간` ,`예상배송기간` 의 IQR)
    - [Items:](https://www.notion.so/1a1cd66266a080b9af8fe1056a1d9628?pvs=21) 중복되는 oredr_item_id 를 sum 집계 후 count 열로 요약하여 중복 제거
    - [dim_date:](https://www.notion.so/1a9cd66266a0806cadb1e4158f8cf140?pvs=21)  timestamp 형식의 날짜 데이터를 month 별로 group하여 효율적 분석 도모
    - geolocation 데이터에 위-경도가 맞지 않아 주도를 기준으로 500km 이상 떨어져 있는 좌표를 이상치로 매핑한 후 knn 분류기를 사용하여 보정 , order 및 item 데이터에 중복데이터 병합
</aside>

# **2. 본론**

<aside>

<aside>

## 1. 리뷰데이터 분석을 통한 문제 설정

- 브라질 지역별 배송시간과 소비자 만족 분석
- 분석 목적: 리뷰 점수 정량분석과 리뷰 텍스트 정성분석으로 고객 만족도에 영향을 끼치는 주요 원인을 파악하고자 한다.

### **STEP 1.  리뷰 데이터 내 배송🚚 관련 키워드(긍정/부정) 감성 분석**

**📌요약** 

**👍 긍정적인 리뷰에서는 빠른 배송에 대한 칭찬이 많고**, 좋은 품질에 대한 언급이 많음

👎 부정적인 리뷰에서는 잘못된 제품에 대한 불만, 품질 불량 , 고객 서비스 불만, 배송 중 파손에 대한 언급이 많음  

**📌 비정형 데이터 분석 리뷰** 

1. **감성분석** 

**감정 그룹에 따른 평균 점수 차이**

![image.png](project_readme_image/image%201.png)

**통계적 유의성 확인**

- 감성 분류 그룹 간 리뷰 평점 차이

p-value 0.029196 ( < 0.05)

**배송 키워드에 따른 평균 리뷰 점수 차이**

![image.png](project_readme_image/image%202.png)

**통계적 유의성 확인**

- 키워드 그룹 간 리뷰 평점 차이
 p-value: 0.014541 ( < 0.05)
- 감정 간 리뷰 평점 차이 
p-value: 0.029196 ( < 0.05)
 ✅ 두 값 모두 0.05 미만으로,배송 상태가 고객 만족도에 미치는 영향이 유의미함.

1. **감성분석 - 긍정/부정 주요 키워드 분석**
- **분석에서 “시간”과 관련된 키워드를 중점으로 분석했음**

**[긍정 리뷰 분석 시각화]**

![image.png](project_readme_image/image%203.png)

**[부정 리뷰 분석 시각화]**

![image.png](project_readme_image/image%204.png)

👍 **긍정적인 리뷰**에서는:

- **빠른 배송**에 대한 칭찬이 많음 → "antes prazo", "super rápida", "chegou bem antes"
- **품질이 좋음**을 강조 → "boa qualidade", "ótima qualidade"

👎 **부정적인 리뷰**에서는:

- **잘못된 제품**에 대한 불만 → "produto errado", "produto veio errado"
- **품질 불량** → "péssima qualidade", "baixa qualidade"
- **고객 서비스 불만** → "falta respeito cliente"
- **배송 중 파손** → "produto veio quebrado"

### **STEP 2.  판매자 구매자 주에 따른 배송 기간📆 분석**

- cf. 판매자 / 구매자 주 동일 여부에 따른 평균 배송 기간 차이
    
    ![image.png](project_readme_image/image%205.png)
    
    판매자 / 구매자 주가 다른 경우의 평균 배송 기간(15일)이 판매자 / 구매자 주가 동일한 경우(약 7.9일)보다 긴 것으로 나타남.
    

**📌지역에 따른 평균 배송 시간**

![image.png](project_readme_image/image%206.png)

**📌주요 인사이트**

1. **판매자와 구매자의 주(state)가 다르면 배송 기간이 길어짐**
    - 평균 배송 기간:
        - 다른 주 → 15일
        - 같은 주 → 7.9일
    - 판매자 → 물류회사까지의 소요 시간은 큰 차이 없음.
        - 중서부 출발 물류는 판매자 → 물류회사까지 소요 시간이 김
    - 물류회사 → 고객 배송에서 차이 발생.
2. **판매자와 구매자가 같은 주에 있을 때 예상보다 배송 지연 빈번**
    - 🚚 실제 배송 소요 시간이 예상보다 긴 비율이 높음.

**📌 세부 내용**

1. 중서부 → 북부, 중서부 → 북동부 배송 지연 多
    - 판매자 → 물류: 7~8일
    - 물류 → 고객: 11일 이상
    - 총 배송 기간: 18~20일 이상
    
    **⇒  개선 필요: 중서부 출발 물류 프로세스 최적화**
    
2. **지역별 배송 차이 큼 (특히 북부 지역 느림)** 
    - 북부 지역 평균 배송 기간:  평균 13일 이상 소요 (전체 평균 8.03일 대비, + 5일)

### **STEP 3. 배송 지연과 리뷰 점수 분석**

- 배송 지연의 정의: 실제 배송 완료 시각이 배송 예정 시각을 초과한 경우
    
    (order_estimated_delivery_date < order_delivered_customer_date)
    

**📌주요 인사이트**

✅  **빠른 배송은 고객 만족도를 높이고, 지연 및 미수령은 부정적 평가를 유발하는 핵심 요인임**.

- 리뷰 점수가 2점 이하로 떨어짐.
- 배송 시간이 **1.5일 이상 단축될 경우 리뷰 점수가 증가하는 경향**.

**📌 배송 키워드에 따른 평균 배송일, 리뷰 점수 차이 비교** 

![image.png](project_readme_image/image%207.png)

- **빠른 배송 리뷰**
    - 평균 배송일: 8.66일 (전체 평균 10.13일 대비 -1.47일)
    - 리뷰 점수: 4.84
- **배송 지연 및 미수령 리뷰**
    - 평균 배송일: 12.02일 (전체 평균 10.13일 대비 +1.89일)
    - 리뷰 점수: 1.83
- **배송 상태가 고객 만족에 미치는 영향**
    - 빠른 배송 리뷰 점수(4.84)는 배송 지연 리뷰 점수(1.83)의 2.6배
    

## **2.  머신러닝으로 소비자 만족도의 주요 원인 파악 및 검증**

**📌주요 인사이트 요약** 

- **배송 기간에 영향을 미치는 변수들의 중요도 분석**
    - 물류회사의 위치에 큰 영향을 받음

- **물류회사 위치의 중요성:**
    
    ML 모델이 공통적으로 해당 변수를 중요하게 평가함에 따라,
    
    **물류회사의 위치 조정**을 통해 배송 시간을 단축하고 배송 지연을 감소시킬 수 있음.
    
- **최적의 물류센터 위치 선정:**
    
    이를 통해 소비자 만족도를 높이는 방향으로 최적의 물류회사 위치 선정을 목표로 함
    

**📌검증 과정**

- **배송 시간 구성:**
    
    배송 기간은 **판매자 → 물류회사 (seller_to_carrier)** 와 **물류회사 → 고객 (carrier_to_customer)** 로 구분됨.
    
- **중요 변수 도출:**
    
    TabNet, RF, XGB, LGBM 모델의 변수 중요도 분석 결과,
    
    - **carrier_to_customer** (물류회사 → 고객 배송 시간)
    - **customer_lat, customer_lng** (고객의 위경도 데이터)
    
    가 가장 큰 영향을 미침.
    

![image.png](project_readme_image/image%208.png)

![image.png](project_readme_image/image%209.png)

![image.png](project_readme_image/image%2010.png)

![image.png](project_readme_image/image%2011.png)

## 3.  배송 시간 단축을 위한 물류센터의 위치 선정 및 제안

### **📌 동부 / 서부 물류센터 위치 선정 과정**

**Step 1.** 

- 배경: 기존의 데이터에는 초기 물류 센터 없음
- 브라질의 도로 / 철로 인프라 맵을 참고해 북부 / 중서부를 서부, 북동부 / 남동부 / 남부를 동부로 그룹화하여 동·서부 물류 센터 위치 2곳을 선정하기로 함
    
    
    ![image.png](project_readme_image/image%2012.png)
    
    ![image.png](project_readme_image/image%2013.png)
    
- 각 권역 그룹 구매자의 위·경도 중앙값을 기준으로 물류센터 위치를 선정
- 최초 물류센터 위치
    - 동부 : 위도 -22.846086, 경도 -44.142523
    - 서부 : 위도 -15.807180, 경도 -49.236702

**Step 2.** 

- 최초 동/서부 물류센터 위·경도 데이터를 기준으로
    - 구매자 → 판매자 거리가 구매자 → 물류센터 거리보다 짧은 행을 제외한 뒤
    (이 경우 물류센터를 거치지 않고 구매자 - 판매자끼리 직접 배송하는 것이 
    더 효율적이기 때문)
    각 권역 그룹 구매자의 위·경도 중앙값 재계산

**Step 3.** 

- Step 2.를 중앙값이 변동하지 않을 때까지 반복

### **📌 선정한 위치로 물류센터 수정 후 예상 효과 :  평균 배송 기간 및 권역별 개선**

<초기값: 임시 물류센터 위치>

동부는 리우데자네이루 근처에, 서부는 브라질리아 근처에 위치

- 동부 : 위도 -22.846086, 
           경도 -44.142523
- 서부 : 위도 -15.807180, 
           경도 -49.236702

![image (6).png](project_readme_image/image_(6).png)

<선정한 물류센터 위치>

(반복 실행 횟수 : 7회)

- 동부 : 위도 -19.960875, 
           경도 -43.124572
- 서부 : 위도 -15.799802, 
           경도 -49.208182

![image.png](project_readme_image/image%2014.png)

### **📌** 전체 평균 배송 기간 개선

- **수정 전 평균 배송일:** 12.79일
- **수정 후 평균 배송일:** 11.60일
- **단축 효과:** 1.19일 (약 9.30% 단축)

### **📌**  권역별 개선 예상 효과

아래 표는 판매자 지역과 고객 지역의 조합별로, 수정 전후 예상 배송 기간과 개선 효과를 비교 

![image.png](project_readme_image/image%2015.png)

- 전체적으로 평균 **1.19일**의 배송 기간 단축 효과가 예상됨.
- 특히, **북동부 판매자**와 **북부 구매자**가 물류 센터를 통한 배송 개선 혜택을 크게 볼 것으로 기대됨
- 북부 → 중서부는 물류센터로 인한 예상 배송 기간이 오히려 0.11일 증가했으나, 기존 평균 배송 기간이 다른 그룹 대비 평균 4일로 매우 짧고 예상 증가일도 0.11일(약 2시간 30분)으로 미미하여 중요도가 낮음

</aside>

</aside>

## 3.  결론 및 전망

<aside>

### **📌  프로젝트 인사이트 요약**

1. **고객 만족도 및 리뷰 분석과의 연계**
    - 빠른 배송("antes prazo") 시 리뷰 점수가 크게 향상되는 반면, 지연 배송("negação recebi") 시 급격히 낮아지는 점수를 토대로, 배송 소요 기간 단축이 곧 고객 만족도 증대로 이어짐을 확인.
2. **고객 만족도를 높이기 위한 제안: 물류회사 위치 재조정 및 배송 예측 로직 업데이트**
    1. 물류 최적화: 중서부 지역의 과도한 판매자 → 물류 이동 시간을 현실적으로 반영해, 효율적 경로 및 물류센터 배치 방안을 마련.
    2. 배송예측로직 업데이트: 기존 로직 대비 실제 배송 지연을 과소평가하지 않도록 로직을 수정하여, 보다 신뢰성 있는 예상 배송 시간을 산출.
3. **물류 최적화 (물류센터 위치 선정) 기대효과**
    - 기존 배송 시스템 대비 물류센터를 통한 배송 시, 평균 12.79일이던 배송 기간을 11.60일(**1.19일 / 9.30% 단축**)로 단축시킬 수 있을 것으로 예상됨 
    특히 상대적으로 교통 인프라가 열악한 중서부 / 북부에 거주하는 구매자들에 대한 평균 배송 기간 단축 효과가 높게 나타남

### **📌 추후 과제 및 회고**

1. 추후 과제 
    - 실무에서는 물류 센터 건설로 예상되는 배송 기간 단축 효과 및 이를 통한 소비자 만족도 개선이 실제 물류 센터 건설 시 발생하는 비용을 뛰어넘는 실효성이 있는지 타당성 검토가 필요할 것으로 예상됨
    - 향후 지역별 추가 인프라 투자와 배송 경로 최적화를 병행한다면, 배송 기간이 더 단축될 수 있을 것
    - 리뷰분석의 키워드를 “시간”에서 확장하여 “품질” , “파손” 등의 요인을 상품 카테고리 및 지역, 계절과 연관지어서 분석하여 서비스를 개선할 수 있을것 같다.
    - 정확해진 배송 예측 정보를 통해 부정적 리뷰(“negação recebi”)를 줄이고, 긍정적 리뷰(“antes prazo”)를 늘려 고객 만족도를 향상시키는 선순환이 구축될 것
    - ML 기반 정교한 예측 모델을 도입하여 지연 가능성을 사전에 파악하고 보다 빠른 대응이 가능해질 것
2. Next Steps 
    - **가설 1:** 배송 소요 기간(평균 배송일)와 고객 리뷰 점수 간의 직접적 인과관계가 존재한다.
    - **가설 2:** 소비자 만족(리뷰 내용, 리뷰 점수)의 주요 독립변수는 ‘배송 지연’이다.
    - **검증 방법:** Random Forest, LightGBM 등 ML 기법을 사용하여, 개선된 배송 데이터를 기반으로 실제 리뷰 점수 변화를 추적하고 예측 정확도 및 변수 중요도를 평가.
</aside>

