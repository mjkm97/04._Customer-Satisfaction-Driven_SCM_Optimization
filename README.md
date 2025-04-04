#  최적 물류센터 위치 제안 프로젝트  
![image](https://github.com/user-attachments/assets/7fec0dee-7b47-43c6-99bd-e7335e1c1aef)

브라질 Olist 데이터를 활용한 소비자 만족도 개선 전략  

---

##  프로젝트 정보

| 이름       | 역할                                                         |
|------------|--------------------------------------------------------------|
| **양현우** | DW 및 데이터 마트 설계, 데이터 전처리, NLP, 머신러닝         |
| **박병제** | 데이터 시각화, 회귀분석, 도메인 리서치                        |
| **김민주** | 데이터 시각화, EDA, 도메인 리서치,기획 및 문서화 리드                             |

> 본 프로젝트는 **데이터리안 실전반 37기 데이터 분석 프로젝트**로 진행되었습니다.

---

##  프로젝트 개요

### ▪️ 문제 정의
- Olist 이커머스 데이터를 분석한 결과, **배송 지연**이 소비자 만족도 하락의 핵심 원인으로 도출됨.
- 리뷰 분석 결과, 배송 소요 기간이 리뷰 점수에 **직접적인 영향**을 미치는 것으로 나타남.
  
### ▪️ 목표
- 리뷰 및 배송 데이터를 분석하여, **고객 만족도에 영향을 주는 주요 변수 도출**
- **배송 지연 해결을 위한 최적의 물류센터 위치 제안**, 개선 효과를 **정량적으로 수치화**

---

##  데이터 구조 및 설계 철학

### ▪️ 설계 개요
- 원본 데이터는 중복 및 결측, 비정규화 → **분석/모델링 비효율적**
- **Fact / Dimension / Mart 테이블 분리**로 **분석 최적화 및 확장성 확보**
<p float="left">
  <img src="https://github.com/user-attachments/assets/84bf9893-f5b5-495f-9951-f14bcbacf8bf" width="60%" />
  <img src="https://github.com/user-attachments/assets/ad0b2ff6-5729-4808-8299-ed5a9212b29b" width="30%" />
</p>

| 테이블명           | 설명                                                        |
|-------------------|-------------------------------------------------------------|
| `dim_seller`      | 판매자 정보 통합. 위경도, 지역 기반 분석                   |
| `dim_customer`    | 고객 정보 통합. 거리 계산 및 지역 분석 목적                 |
| `fact_orders`     | 주문 중심 데이터. 배송 상태, 지연 여부                     |
| `fact_items`      | 상품별 가격, 배송 마감 기한, 수량                           |
| `mart_orders`     | `fact_orders` + `fact_items` 통합.                           |
| `overall_mart`    | `mart_orders` + `dim_seller/customer` → 분석용 통합 테이블   |
| **`mart_review`** | 최종 테이블. `overall_mart` + 리뷰 데이터                   |

---

### ▪️ 설계 이유 및 기대 효과

| 설계 요소          | 설계 목적 및 고려 사항                                                              |
|-------------------|-------------------------------------------------------------------------------------|
| Fact 테이블 분리  | 주문 단위/상품 단위 데이터 분리로 확장성 및 모듈화 확보                             |
| Dimension 테이블  | 위경도 기반 거리 계산 및 지역 분석 용이                                              |
| Mart 테이블 설계  | 분석 효율성 위해 필요한 테이블만 선택적 조인 → 쿼리 최적화, 비용 최소화               |
| 최종 mart_review  | 리뷰 데이터 포함 비정형 텍스트 전처리 후 통합 → 머신러닝 및 텍스트 분석 최적화        |

- 정규화 → 비정규화 설계로 Spark / SQL 환경에서 **조인 최적화 및 처리 효율성 증대**  
- 분석 및 모델링 시 **데이터 가독성 향상**, **확장성 및 유지보수 용이**

---
## 전처리
  - 코드 : (https://github.com/YangHyunu/olist-data-driven-logistics/tree/main/preprocessing_analysis)
  - 설명 : [https://www.notion.so/1a1cd66266a0806e8960e453cb90d3e3](https://heathered-citron-b6f.notion.site/1a1cd66266a0806e8960e453cb90d3e3?pvs=4)

#### 전처리 예시
위도/경도와 지역 정보(`state`) 불일치 문제(약 1만건) Isolation Forest로 탐지하고
![image](https://github.com/user-attachments/assets/862e8f50-0f1d-4cd1-850b-163432ad4d9f)

![image](https://github.com/user-attachments/assets/90adc552-6745-4f32-b2fe-573c49bfff13)

Random Forest Classifier를 사용해 올바른 지역 정보를 예측 하여 보정
| Index   | 위도     | 경도     | 원래 State | 예측 State |
|---------|----------|----------|------------|-------------|
| 345301  | -1.8884  | -55.1214 | SP         | PA          |
| 513631  | 41.6140  | -8.4116  | RJ         | PE          |

---
##  리뷰 분석 및 배송 지연 문제 정의

### ▪️ 감성 분석 (RoBERTa 모델 활용)  
- 다국어 리뷰 감성 분석: Huggingface RoBERTa fine-tuned 모델 사용
  -  XLM-Roberta 모델을 포르투갈어 트위터/X로 학습한 모델이라 리뷰데이터 감성분석에서 제 성능을 보이지 못했음
  -  과도한 어근추출을 완화하여 단어의 원래 의미를 보존하여 해결결
- 배송 관련 키워드 기반 감정 분석 → **긍/부정 리뷰 점수 차이 명확**  
  - 빠른 배송 리뷰 평균 **4.84점**
  - 배송 지연 리뷰 평균 **1.83점**


![image](https://github.com/user-attachments/assets/9bd83231-c640-4813-a1d9-64592aa6e557)
<p float="left">
  <img src="https://github.com/user-attachments/assets/df22b9f8-3285-447e-b801-0f3aeeccebc2" width="45%" />
  <img src="https://github.com/user-attachments/assets/bdfdc2c3-081f-4302-acc2-15d3eb29f721" width="45%" />
</p>

## 🚚 배송 소요 기간 분석

| 조건               | 평균 배송일 |
|--------------------|-------------|
| 판매자-고객 동일 주 | 7.9일       |
| 서로 다른 주       | 15일        |

- 판매자-고객 거리 및 물류 경로 → **배송 지연 핵심 요인**  
- **북부/중서부 지역** 배송 지연 심각

<p float="left">
  <img src="https://github.com/user-attachments/assets/669592b7-fd84-4935-8fcf-2e9df17970a8" width="45%" />
  <img src="https://github.com/user-attachments/assets/fd680ea3-c0f3-4fd6-bf8e-4b82b5c58a80" width="45%" />
</p>

---
##  머신러닝 분석 및 변수 도출

### ▪️ 모델 및 분석 방식

| 모델               | 특징 및 활용 목적                                         |
|--------------------|----------------------------------------------------------|
| TabNet             | 범주형+수치형 혼합 데이터 최적화                          |
| Random Forest      | 변수 중요도 직관적, 해석 용이                             |
| XGBoost, LGBM      | 예측 성능 및 변수 해석력 탁월                             |

### ▪️ 주요 변수 중요도

| 변수                   | 설명                                        | 중요도 |
|------------------------|---------------------------------------------|--------|
| `carrier_to_customer`  | 물류회사 → 고객 배송 시간                   | ★★★★★ |
| `customer_lat/lng`     | 고객 위경도 데이터                         | ★★★★☆ |
| `freight_value`        | 배송비                                     | ★★★☆☆ |

<p float="left">
  <img src="https://github.com/user-attachments/assets/db8dbc61-ff0d-4c8e-884e-2cd01346a64c" width="45%" />
  <img src="https://github.com/user-attachments/assets/9d8b7e77-4d51-41e5-9c0d-0116b1ff1e8c" width="45%" />
</p>

<p float="left">
  <img src="https://github.com/user-attachments/assets/874bc742-b496-4e8d-aa47-daeb43e832e1" width="45%" />
  <img src="https://github.com/user-attachments/assets/69ed9876-e137-43f0-9e00-c9a0324c93d8" width="45%" />
</p>

---

## 📍 물류센터 위치 최적화 및 효과
### carrier to customer 를 줄이기 위해 , 물류센터의 위치와 고객간의 거리를 최소화하는것을 목표로 함
![image](https://github.com/user-attachments/assets/f0ad168b-860c-4252-a857-944049fea357)

---

### ▪️ 최적화 로직 (KMeans + 군집 기반 접근)


1. 판매자와 고객의 위·경도 평균으로 **초기 허브 위치** 설정
![image](https://github.com/user-attachments/assets/827b0a35-ef48-4194-bfc5-79800bbd2da3)

2. **주문 수량(quantity)을 가중치**로 거리 차이 최소화 → 물류 허브 최적화
![image](https://github.com/user-attachments/assets/190f2435-22c3-4637-b182-fa35d623a673)

Q: "각 주(State)마다 물류센터를 두는 것이 정말 최적인가?"
> 경우에 따라 특정 주(State)들이 가까운 위치에 있을 수 있음. 예를 들어, SP(상파울루)와 RJ(리우데자네이루)는 가까우므로 하나의 물류센터로 통합하는 것이 더 효율적일 수도 있음.

A : K-Means 클러스터링을 활용하여 물류센터 개수를 최적화.
3. **Elbow Method**로 최적 클러스터 수(K=5) 결정  
![image](https://github.com/user-attachments/assets/44f7797d-cc8e-4da7-9640-974ad7c74594)

4. KMeans 클러스터링으로 **최적 물류 허브 중심 좌표 도출**

---

### ▪️ 최종 물류 허브 중심 좌표 (K=5 기준)

| 클러스터 | 위도(Lat)       | 경도(Lng)       |
|----------|-----------------|-----------------|
| 1        | -21.2264        | -43.0738        |
| 2        | -14.8082        | -50.7902        |
| 3        |  -7.6275        | -39.2443        |
| 4        | -27.2574        | -50.9832        |
| 5        | -23.0130        | -47.0728        |

---

### ▪️ 최적화 효과

| 비교           | 평균 배송일 |
|----------------|-------------|
| 기존           | 12.79일     |
| 최적화 후      | 11.60일     |
| 개선           | **1.19일 감소 (9.3%)** |

| 물류센터 위치 최적화 이전 | 물류센터 위치 최적화 이후 |
|------------------------|-------------------------|
| ![image](https://github.com/user-attachments/assets/b6ff6b51-c805-4418-a59d-9453fb1510ef)| ![image](https://github.com/user-attachments/assets/9994ca24-4d95-4b0d-83ab-b98e12bc85e8)|

---
##  기술 스택 및 활용 방식

| 도구/기술      | 활용 내용                                                                 |
|----------------|---------------------------------------------------------------------------|
| **Python**     | 데이터 전처리, 머신러닝(NLP/회귀 분석), 시각화 기반 분석 수행              |
| **PySpark**    | 데이터 정제 및 DW/데이터 마트 설계, 대용량 주문 데이터 전처리 및 처리 효율화 |
| **Pandas**     | EDA 및 통계 분석, 전처리 보완, 시각화                                     |
| **Spark SQL**  | 테이블 간 조인 및 집계, 배송 지연 분석 등 SQL 기반 효율적 분석 수행       |
| **Tableau**    | 주요 분석 결과 및 인사이트 시각화                                         |
| **Docker**     | 환경 컨테이너화, 재현 가능한 분석 환경 구축                               |

---

### 🐳 Docker 실행 방법

```bash
# 내 Docker Hub에서 이미지 다운로드
docker pull yanghyeonwoo/spark_olist:latest

# 컨테이너 실행
docker run -it --rm yanghyeonwoo/spark_olist:latest
```

---

## 📁 프로젝트 폴더 구성 

```
Olist/
│
├── dim_table/               # Dimension 테이블 (고객, 판매자 정보 등)
├── fact_table/              # Fact 테이블 (주문, 상품별 주문 정보)
├── mart_table/              # 데이터 마트 (분석 최적화 테이블)
├── preprocessing_analysis/  # 데이터 전처리 및 기초 분석 코드
│
├── model/                   # 머신러닝 모델 및 결과 저장
├── raw_data/                # 원본 데이터 (csv 등)
│
├── script/                  # 실행 스크립트 및 최종 물류 허브 산출 코드
├── spark-warehouse/         # Spark 작업 디렉토리 (임시 저장소)
│
├── README.md                # 프로젝트 설명 문서
│
├── 리뷰데이터 분석.ipynb       # 리뷰 감성 분석 (NLP)
├── 리뷰데이터&CRM.ipynb      # 리뷰 및 CRM 기반 분석
├── 물류&리뷰데이터.ipynb      # 물류 데이터 + 리뷰 연계 분석
├── 물류회사_위치.ipynb        # 최적 물류 허브 위치 산출
├── 배송A-B.ipynb             # 배송 거리 및 시간 비교 분석
본 데이터 (csv 등)
├── script/                  # 실행 스크립트 및 모듈화 코드
├── spark-warehouse/         # Spark 작업 디렉토리
└── README.md                # 프로젝트 설명 문서
```                       
---

## 핵심 요약
배송 지연은 리뷰 점수 하락의 주요 원인 → 리뷰 감성 분석 및 ML 분석을 통해 검증
물류센터 최적화를 통해 평균 배송일 1.19일(9.3%) 단축 → 고객 만족도 향상 기대
특히 북부·중서부 지역 고객의 배송 시간 개선 효과가 두드러짐
## 회고 및 Next Steps
실무 확장 고려: 물류센터 신설에 따른 비용 대비 효과 타당성 검토 필요
리뷰 분석 확장: 배송 외에도 “품질”, “파손” 등 키워드 분석으로 서비스 개선 가능
고도화 방안: ML 기반 배송 지연 예측 모델 도입으로 사전 대응 가능
- 향후 검증 과제:
  - 가설 1. 배송 기간과 리뷰 점수 간 직접적 인과관계 존재
  - 가설 2. 고객 만족도 주요 요인은 ‘배송 지연’
#### 검증 방법: Random Forest, LightGBM 기반 리뷰 점수 예측 및 변수 중요도 분석

