# Database Design

Database

```
crm_multiagent
```

## customers

```json
{
    "_id":"CUS0001",

    "full_name":"Nguyễn Văn A",

    "phone":"0912345678",

    "email":"vana@gmail.com",

    "customer_state":"HCM"
}
```

---

## orders

```json
{
    "_id":"ORD0001",

    "customer_uid":"CUS0001",

    "order_value":2500000,

    "payment_type":"credit_card",

    "delivery_days":5,

    "review":"Máy đẹp nhưng giao hơi chậm."
}
```

---

## reports

Lưu báo cáo được sinh bởi Report Agent.

---

## agent_logs

Lưu log toàn bộ Agent.

---

## Quan hệ

customers

↓

orders

↓

reports

↓

agent_logs