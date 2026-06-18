# API Document

## POST

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