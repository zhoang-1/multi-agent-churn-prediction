# Project Overview

# Hệ thống Multi-Agent AI phân tích trải nghiệm khách hàng và dự đoán rời bỏ trong thương mại điện tử

## Mục tiêu

Đồ án xây dựng một hệ thống Multi-Agent AI nhằm hỗ trợ doanh nghiệp thương mại điện tử phân tích khách hàng và đưa ra quyết định chăm sóc khách hàng dựa trên Machine Learning và Large Language Model.

Hệ thống có khả năng:

- Quản lý khách hàng
- Phân tích trải nghiệm khách hàng
- Dự đoán khả năng rời bỏ
- Sinh báo cáo tự động
- Đề xuất chiến lược CRM

---

## Công nghệ

- Python
- FastAPI
- MongoDB
- LangGraph
- Google Gemini
- Scikit-learn
- XGBoost
- Pandas
- NumPy

---

## Hai bộ dữ liệu

### Dataset 1

Olist Brazilian E-commerce Dataset

Mục đích:

Huấn luyện Sentiment Model

---

### Dataset 2

Online Retail II Dataset

Mục đích

Huấn luyện Churn Prediction Model

---

## Kiến trúc tổng thể

                    User

                    ↓

                    FastAPI

                    ↓

                    MongoDB

                    ↓

                Data Agent

                   
↓                                ↓  

Sentiment Agent             Churn Agent

↓



Report Agent

↓

Action Agent