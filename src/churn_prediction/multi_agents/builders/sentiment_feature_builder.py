import numpy as np
import pandas as pd

class SentimentFeatureBuilder:

    def build(self, customer_profile):

        orders = customer_profile["orders"]

        features = {}

        # Sinh nhóm feature RFM
        features.update(self._build_rfm(orders))

        # Sinh nhóm feature giao hàng
        features.update(self._build_delivery(orders))

        # Sinh nhóm feature thanh toán
        features.update(self._build_payment(orders))

        # Sinh nhóm feature review
        features.update(self._build_review(orders))

        # Sinh nhóm feature xu hướng mua
        features.update(self._build_trend(orders))

        return features
    def _build_rfm(self, orders):
        features = {}

        if len(orders) == 0:
            features["recency"] = np.nan
            features["frequency"] = 0
            features["monetary"] = 0
            return features

        # Tính recency (số ngày kể từ đơn hàng cuối cùng)
        last_order_date = orders["order_date"].max()
        features["recency"] = (pd.Timestamp.now() - last_order_date).days

        # Tính frequency (số đơn hàng)
        features["frequency"] = len(orders)

        # Tính monetary (tổng giá trị đơn hàng)
        features["monetary"] = orders["order_value"].sum()

        return features