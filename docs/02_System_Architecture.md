# System Architecture

## Kiến trúc tổng thể

```
               User
                 │
                 ▼
            FastAPI Server
                 │
                 ▼
             MongoDB
                 │
                 ▼
          Data Agent
                 │
      Customer Profile
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
Sentiment Agent      Churn Agent
      │                     │
      └──────────┬──────────┘
                 ▼
           Report Agent
                 │
                 ▼
           Action Agent
                 │
                 ▼
             API Response
```

## Thành phần

### FastAPI

- REST API
- Validation
- Routing

---

### MongoDB

Lưu:

- Customers
- Orders
- Reports
- Agent Logs

---

### LangGraph

Điều phối hoạt động của toàn bộ Agent.

                        User
                          │
                          ▼
                     FastAPI
                          │
                          ▼

                  CustomerDataAgent

                          │

                MongoDB (Customers)

                MongoDB (Orders)

                          │

                          ▼

                  Customer Profile

                          │

             ┌────────────┴────────────┐

             ▼                         ▼

    OlistFeatureBuilder      ChurnFeatureBuilder

             ▼                         ▼

      Sentiment Agent          Churn Agent

             │                         │

             └────────────┬────────────┘

                          ▼

                    Report Agent

                          ▼

                    Action Agent

                          ▼

                    JSON Response

                          ▼

                      Dashboard