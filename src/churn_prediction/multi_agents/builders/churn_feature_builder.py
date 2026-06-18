import pandas as pd
from datetime import datetime


class ChurnFeatureBuilder:

    def build(self, customer_profile: dict):

        orders = customer_profile.get("orders", [])

        if not orders:
            return {}

        df = pd.DataFrame(orders)

        now = datetime.now()

        last_order = pd.to_datetime(
            df["order_date"]
        ).max()

        recency = (
            now - last_order
        ).days

        frequency = len(df)

        monetary = (
            df["order_value"]
            .sum()
        )

        avg_order_value = (
            df["order_value"]
            .mean()
        )

        avg_delivery_days = (
            df["actual_delivery_days"]
            .mean()
        )

        avg_items = (
            df["num_items"]
            .mean()
        )

        avg_installments = (
            df["payment_installments"]
            .mean()
        )

        credit_card_ratio = (
            (df["payment_type"] == "credit_card")
            .mean()
        )

        boleto_ratio = (
            (df["payment_type"] == "boleto")
            .mean()
        )

        return {

            "Recency":
                recency,

            "Frequency":
                frequency,

            "Monetary":
                monetary,

            "AvgOrderValue":
                avg_order_value,

            "AvgDeliveryDays":
                avg_delivery_days,

            "AvgItems":
                avg_items,

            "AvgInstallments":
                avg_installments,

            "CreditCardRatio":
                credit_card_ratio,

            "BoletoRatio":
                boleto_ratio
        }