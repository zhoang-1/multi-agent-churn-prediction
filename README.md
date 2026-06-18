# Hệ thống Multi-Agent AI phân tích trải nghiệm khách hàng và dự đoán rời bỏ trong thương mại điện tử

> Graduation Project
>
> Multi-Agent AI System for Customer Experience Analysis and Customer Churn Prediction in E-commerce

---

# 1. Giới thiệu

Đồ án xây dựng một hệ thống Multi-Agent AI nhằm hỗ trợ doanh nghiệp thương mại điện tử:

- Phân tích trải nghiệm khách hàng.
- Dự đoán khả năng khách hàng rời bỏ (Customer Churn).
- Tổng hợp báo cáo tự động bằng Large Language Model (LLM).
- Đề xuất chiến lược chăm sóc khách hàng và giữ chân khách hàng.

Hệ thống sử dụng:

- Machine Learning
- Large Language Model (Gemini)
- LangGraph
- FastAPI
- MongoDB

Toàn bộ hệ thống hoạt động theo mô hình Multi-Agent.

---

# 2. Mục tiêu

Hệ thống có khả năng:

- Quản lý dữ liệu khách hàng
- Quản lý lịch sử đơn hàng
- Sinh feature tự động
- Phân tích trải nghiệm khách hàng
- Dự đoán Customer Churn
- Sinh báo cáo bằng AI
- Đề xuất chiến lược CRM tự động

---

# 3. Công nghệ sử dụng

## Backend

- Python 3.12
- FastAPI

---

## Database

MongoDB

Lưu trữ:

- Customer
- Orders
- Reviews
- Reports
- Agent Logs

---

## Machine Learning

scikit-learn

Các mô hình sử dụng:

### Sentiment Model

- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost

### Churn Model

- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost

---

## Large Language Model

Google Gemini

Sử dụng cho:

- Report Agent
- Action Agent

---

## Multi-Agent Framework

LangGraph

---

## Data Processing

- Pandas
- NumPy
- Scikit-learn

---

# 4. Dataset

Hệ thống sử dụng hai bộ dữ liệu độc lập.

---

## Dataset 1

Olist Brazilian E-commerce Dataset

Mục đích:

- Phân tích trải nghiệm khách hàng
- Huấn luyện Sentiment Model

Các feature được sinh gồm:

- Recency
- Frequency
- Monetary
- Delivery Time
- Freight
- Payment
- Category
- Customer State
- ...

Output:

Customer Experience

---

## Dataset 2

Online Retail II Dataset

Mục đích:

Huấn luyện Churn Prediction Model.

Output:

Customer Churn Probability

---

# 5. Kiến trúc hệ thống

```

User
│
▼
FastAPI
│
▼
MongoDB
│
▼
LangGraph
│
├──────────────┐
│ │
▼ ▼
Sentiment Churn
│ │
└──────┬───────┘
▼
Report
│
▼
Action

```

---

# 6. Kiến trúc MongoDB

Database:

```

crm_multiagent

```

Collections:

```

customers

orders

reports

agent_logs

```

---

## customers

Lưu thông tin khách hàng.

Ví dụ:

```json
{
    "_id": "CUS0001",
    "full_name": "Nguyễn Văn A",
    "phone": "0912345678",
    "email": "vana@gmail.com",
    "customer_state": "HCM"
}
```

---

## orders

Lưu toàn bộ lịch sử đơn hàng.

Ví dụ:

```json
{
    "_id":"ORD0001",

    "customer_uid":"CUS0001",

    "order_value":2500000,

    "payment_type":"credit_card",

    "delivery_days":5,

    "review":"Sản phẩm tốt nhưng giao hơi chậm."
}
```

---

## reports

Lưu báo cáo AI.

Ví dụ

```json
{
    "customer_uid":"CUS0001",

    "report":"..."
}
```

---

## agent_logs

Lưu log hoạt động của từng Agent.

---

# 7. Kiến trúc thư mục

```

project

│

├── app

│ ├── api

│ ├── database

│ ├── models

│ ├── services

│ ├── agents

│ ├── builders

│ ├── prompts

│ ├── config

│ ├── graph

│ └── state

│

├── datasets

│ ├── olist

│ └── online_retail

│

├── notebooks

│

├── trained_models

│

├── README.md

│

└── main.py

```

---

# 8. Machine Learning Pipeline

```

Dataset

↓

Cleaning

↓

EDA

↓

Feature Engineering

↓

Train/Test Split

↓

Training

↓

Evaluation

↓

Best Model

↓

Save Model (.pkl)

```

---

# 9. Unified Customer Database

Hai bộ dataset chỉ sử dụng để huấn luyện mô hình.

Sau khi train hoàn tất:

```

Olist

↓

Sentiment Model (.pkl)

```

```

Online Retail II

↓

Churn Model (.pkl)

```

Khi hệ thống hoạt động:

Khách hàng mới sẽ được lưu vào MongoDB.

MongoDB trở thành nguồn dữ liệu duy nhất phục vụ inference.

---

# 10. Multi-Agent System

Hệ thống gồm 5 Agent.

---

## Agent 1

Data Agent

Chức năng

- Nhận dữ liệu từ FastAPI
- Kiểm tra khách hàng
- Lưu MongoDB
- Đọc lịch sử mua hàng
- Sinh Customer Profile

Output

```

Customer Profile

```

---

## Agent 2

Sentiment Agent

Input

Customer Profile

Nhiệm vụ

- Sinh feature theo Olist
- Load Sentiment Model
- Predict

Output

```json
{
    "label":"Negative",
    "confidence":0.87
}
```

---

## Agent 3

Churn Agent

Input

Customer Profile

Nhiệm vụ

- Sinh feature theo Online Retail II
- Predict Churn

Output

```json
{
    "risk":"High",

    "probability":0.78
}
```

---

## Agent 4

Report Agent

Sử dụng:

Google Gemini

Input

- Customer Profile
- Sentiment Result
- Churn Result

Output

Báo cáo tổng hợp.

Ví dụ:

- Đánh giá khách hàng
- Phân tích trải nghiệm
- Phân tích nguy cơ churn

---

## Agent 5

Action Agent

Sử dụng:

Google Gemini

Input

- Customer Profile
- Report
- Sentiment
- Churn

Output

Kế hoạch CRM.

Bao gồm

- Hành động ngay
- Hành động ngắn hạn
- Hành động dài hạn

---

# 11. Luồng hoạt động

```

User nhập đơn hàng

↓

FastAPI

↓

MongoDB

↓

Data Agent

↓

Customer Profile

↓

Sentiment Agent

↓

Churn Agent

↓

Report Agent

↓

Action Agent

↓

FastAPI Response

```

---

# 12. API

POST

```

/predict

```

Input

```json
{

"full_name":"Nguyễn Văn A",

"phone":"0912345678",

"email":"vana@gmail.com",

"order_value":2500000,

"payment_type":"credit_card",

"delivery_days":5,

"review":"Máy đẹp nhưng giao hơi chậm."

}
```

Response

```json
{

"customer_profile":{},

"sentiment":{},

"churn":{},

"report":"...",

"action":"..."

}
```

---

# 13. LangGraph

```

START

↓

Data Agent

↓

┌───────────────┐

│ │

▼ ▼

Sentiment Churn

│ │

└───────┬───────┘

↓

Report

↓

Action

↓

END

```

---

# 14. Mục tiêu mở rộng

- Dashboard quản trị
- Realtime Prediction
- Recommendation System
- RAG
- Voice AI
- AI Customer Support
- Multi-modal AI
- AI CRM Platform

---

# 15. Kết luận

Hệ thống kết hợp Machine Learning và Large Language Model theo kiến trúc Multi-Agent nhằm:

- Phân tích hành vi khách hàng.
- Dự đoán nguy cơ rời bỏ.
- Sinh báo cáo tự động.
- Hỗ trợ doanh nghiệp đưa ra quyết định chăm sóc khách hàng nhanh chóng và hiệu quả.

Kiến trúc tách biệt giữa quá trình huấn luyện mô hình (Offline) và quá trình suy luận (Online), giúp hệ thống dễ mở rộng, dễ bảo trì và phù hợp triển khai trong các bài toán thương mại điện tử thực tế.