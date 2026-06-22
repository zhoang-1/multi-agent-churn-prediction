customer_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "customer_id",
            "email",
            "phone",
            "full_name",
            "address",
            "created_at",
            "updated_at"
        ],
        "properties": {
            "customer_id": {
                "bsonType": "string",
                "description": "Unique customer id"
            },
            "email": {
                "bsonType": "string"
            },
            "phone": {
                "bsonType": "string"
            },
            "full_name": {
                "bsonType": "string"
            },

            "address": {
                "bsonType": "object",
                "required": [
                    "street",
                    "ward",
                    "district",
                    "city"
                ],
                "properties": {
                    "street": {
                        "bsonType": "string"
                    },
                    "ward": {
                        "bsonType": "string"
                    },
                    "district": {
                        "bsonType": "string"
                    },
                    "city": {
                        "bsonType": "string"
                    }
                }
            },

            "created_at": {
                "bsonType": "date"
            },

            "updated_at": {
                "bsonType": "date"
            },

            "total_orders": {
                "bsonType": "int",
                "minimum": 0
            },

            "total_spent": {
                "bsonType": [
                    "double",
                    "int",
                    "decimal"
                ],
                "minimum": 0
            },

            "last_order_date": {
                "bsonType": "date"
            }
        }
    }
}