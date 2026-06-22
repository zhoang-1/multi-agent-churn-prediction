order_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "order_id",
            "customer_id",
            "order_date",
            "order_status",
            "payment",
            "delivery",
            "items",
            "created_at",
            "updated_at"
        ],
        "properties": {

            "order_id": {
                "bsonType": "string"
            },

            "customer_id": {
                "bsonType": "string"
            },

            "order_date": {
                "bsonType": "date"
            },

            "order_status": {
                "enum": [
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                    "returned",
                    "canceled"
                ]
            },

            "payment": {
                "bsonType": "object",
                "required": [
                    "method",
                    "installments",
                    "total_payment"
                ],
                "properties": {

                    "method": {
                        "bsonType": "string"
                    },

                    "installments": {
                        "bsonType": "int",
                        "minimum": 1
                    },

                    "total_payment": {
                        "bsonType": [
                            "double",
                            "int",
                            "decimal"
                        ]
                    },

                    "payment_sequence": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object"
                        }
                    }
                }
            },

            "delivery": {
                "bsonType": "object",
                "required": [
                    "estimated_days",
                    "actual_days",
                    "freight_value"
                ],
                "properties": {

                    "estimated_days": {
                        "bsonType": "int"
                    },

                    "actual_days": {
                        "bsonType": "int"
                    },

                    "delivered_date": {
                        "bsonType": "date"
                    },

                    "delivery_delay": {
                        "bsonType": "int"
                    },

                    "freight_value": {
                        "bsonType": [
                            "double",
                            "int",
                            "decimal"
                        ]
                    }
                }
            },

            "items": {
                "bsonType": "array",
                "minItems": 1,
                "items": {
                    "bsonType": "object",
                    "required": [
                        "product_id",
                        "product_name",
                        "category",
                        "quantity",
                        "unit_price",
                        "total_price"
                    ],
                    "properties": {

                        "product_id": {
                            "bsonType": "string"
                        },

                        "product_name": {
                            "bsonType": "string"
                        },

                        "category": {
                            "bsonType": "string"
                        },

                        "quantity": {
                            "bsonType": "int",
                            "minimum": 1
                        },

                        "unit_price": {
                            "bsonType": [
                                "double",
                                "int",
                                "decimal"
                            ]
                        },

                        "total_price": {
                            "bsonType": [
                                "double",
                                "int",
                                "decimal"
                            ]
                        }
                    }
                }
            },

            "review": {
                "bsonType": "object",
                "properties": {

                    "score": {
                        "bsonType": "int",
                        "minimum": 1,
                        "maximum": 5
                    },

                    "comment": {
                        "bsonType": "string"
                    },

                    "comment_cleaned": {
                        "bsonType": "string"
                    },

                    "answer_time_days": {
                        "bsonType": "int"
                    }
                }
            },

            "created_at": {
                "bsonType": "date"
            },

            "updated_at": {
                "bsonType": "date"
            }
        }
    }
}