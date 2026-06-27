import pandas as pd
import numpy as np
from datetime import datetime

class ChurnFeatureBuilder:
    """
    Xây dựng feature vector cho dự đoán churn từ lịch sử mua hàng.
    Đầu ra có đúng 26 feature số (không bao gồm Customer ID hay ngày tháng).
    """

    def __init__(self, snapshot_date=None):
        """
        Args:
            snapshot_date (datetime, optional): Ngày snapshot để tính recency.
                Nếu không cung cấp, tự động lấy max(InvoiceDate) + 1 ngày.
        """
        self.snapshot_date = snapshot_date

    def build(self, customer_profile):
        """
        Args:
            customer_profile (dict): Chứa key "orders" là list các order.
        Returns:
            dict: Feature vector gồm 26 feature số.
        """

        orders = customer_profile.get("orders", [])

        if not orders:
            return self._empty_features()

        # ==========================================================
        # Flatten orders -> order items
        # ==========================================================
        rows = []

        for order in orders:

            order_id = order.get("order_id")
            order_date = pd.to_datetime(order.get("order_date"), errors="coerce")

            payment = order.get("payment", {})
            order_payment = payment.get("total_payment", 0.0)

            items = order.get("items", [])

            # Nếu đơn hàng không có item
            if not items:
                rows.append({
                    "Invoice": order_id,
                    "InvoiceDate": order_date,
                    "StockCode": None,
                    "Quantity": 0,
                    "Price": 0.0,
                    "Revenue": order_payment
                })
                continue

            # Mỗi item sẽ là một dòng
            for item in items:

                quantity = item.get("quantity", 0)
                price = item.get("unit_price", 0.0)

                revenue = item.get(
                    "total_price",
                    quantity * price
                )

                rows.append({
                    "Invoice": order_id,
                    "InvoiceDate": order_date,
                    "StockCode": item.get("product_id"),
                    "Quantity": quantity,
                    "Price": price,
                    "Revenue": revenue
                })

        df = pd.DataFrame(rows)

        if df.empty:
            return self._empty_features()

        # ==========================================================
        # Chuẩn hóa dữ liệu
        # ==========================================================

        df["InvoiceDate"] = pd.to_datetime(
            df["InvoiceDate"],
            errors="coerce"
        )

        df = df.dropna(subset=["InvoiceDate"])

        if df.empty:
            return self._empty_features()

        df["Quantity"] = pd.to_numeric(
            df["Quantity"],
            errors="coerce"
        ).fillna(0)

        df["Price"] = pd.to_numeric(
            df["Price"],
            errors="coerce"
        ).fillna(0)

        df["Revenue"] = pd.to_numeric(
            df["Revenue"],
            errors="coerce"
        ).fillna(df["Quantity"] * df["Price"])

        # ==========================================================
        # Snapshot Date
        # ==========================================================

        if self.snapshot_date is None:
            snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)
        else:
            snapshot = pd.to_datetime(self.snapshot_date)

        # ==========================================================
        # Feature Engineering
        # ==========================================================

        features = {}

        # -----------------------------
        # RFM
        # -----------------------------
        features["Recency"] = (snapshot - df["InvoiceDate"].max()).days
        features["Frequency"] = df["Invoice"].nunique()
        features["Monetary"] = df["Revenue"].sum()

        order_agg = (
            df.groupby("Invoice")
            .agg(
                order_revenue=("Revenue", "sum"),
                order_items=("Quantity", "sum")
            )
            .reset_index()
        )

        features["avg_order_value"] = order_agg["order_revenue"].mean()
        features["avg_items_per_order"] = order_agg["order_items"].mean()

        # -----------------------------
        # Purchase Behavior
        # -----------------------------
        features["total_quantity"] = df["Quantity"].sum()
        features["total_orders"] = features["Frequency"]

        unique_products = df["StockCode"].nunique()

        features["unique_products_x"] = unique_products
        features["unique_products_y"] = unique_products

        features["unique_purchase_days"] = (
            df["InvoiceDate"].dt.date.nunique()
        )

        features["avg_quantity_per_order"] = (
            features["total_quantity"] / features["total_orders"]
            if features["total_orders"] > 0 else 0
        )

        features["max_order_value"] = order_agg["order_revenue"].max()
        features["min_order_value"] = order_agg["order_revenue"].min()

        # -----------------------------
        # Time Features
        # -----------------------------
        first_date = df["InvoiceDate"].min()
        last_date = df["InvoiceDate"].max()

        features["customer_age_days"] = (
            snapshot - first_date
        ).days

        features["days_since_last_purchase"] = (
            snapshot - last_date
        ).days

        features["purchase_span_days"] = (
            last_date - first_date
        ).days

        unique_dates = (
            df["InvoiceDate"]
            .sort_values()
            .drop_duplicates()
        )

        if len(unique_dates) >= 2:
            features["avg_days_between_orders"] = (
                unique_dates.diff().dt.days.mean()
            )
        else:
            features["avg_days_between_orders"] = 0

        # -----------------------------
        # Revenue
        # -----------------------------
        features["total_revenue"] = features["Monetary"]

        features["avg_revenue_per_item"] = (
            features["total_revenue"] / features["total_quantity"]
            if features["total_quantity"] > 0 else 0
        )

        features["revenue_std"] = (
            order_agg["order_revenue"].std()
            if len(order_agg) > 1 else 0
        )

        features["max_revenue"] = (
            order_agg["order_revenue"].max()
        )

        cutoff = snapshot - pd.Timedelta(days=30)

        features["recent_30d_revenue"] = (
            df[df["InvoiceDate"] >= cutoff]["Revenue"].sum()
        )

        # -----------------------------
        # Product Diversity
        # -----------------------------
        product_counts = df.groupby("StockCode").size()

        features["favorite_product_freq"] = (
            product_counts.max()
            if len(product_counts) > 0 else 0
        )

        features["repeat_product_ratio"] = (
            (product_counts > 1).sum() / len(product_counts)
            if len(product_counts) > 0 else 0
        )

        # -----------------------------
        # Loyalty
        # -----------------------------
        features["customer_lifetime_days"] = (
            last_date - first_date
        ).days

        if features["customer_lifetime_days"] > 0:
            features["purchase_rate"] = (
                features["Frequency"] /
                features["customer_lifetime_days"]
            )
        else:
            features["purchase_rate"] = 0

        # ==========================================================
        # Xử lý NaN
        # ==========================================================

        for key in features:

            if pd.isna(features[key]):
                features[key] = 0

            if isinstance(features[key], np.generic):
                features[key] = features[key].item()

        return features

    def _empty_features(self):
        """Trả về dict với tất cả feature = 0 khi không có order."""
        empty = {
            'Recency': 0,
            'Frequency': 0,
            'Monetary': 0.0,
            'avg_order_value': 0.0,
            'avg_items_per_order': 0.0,
            'total_quantity': 0,
            'total_orders': 0,
            'unique_products_x': 0,
            'unique_products_y': 0,
            'unique_purchase_days': 0,
            'avg_quantity_per_order': 0.0,
            'max_order_value': 0.0,
            'min_order_value': 0.0,
            'customer_age_days': 0,
            'days_since_last_purchase': 0,
            'purchase_span_days': 0,
            'avg_days_between_orders': 0.0,
            'total_revenue': 0.0,
            'avg_revenue_per_item': 0.0,
            'revenue_std': 0.0,
            'max_revenue': 0.0,
            'recent_30d_revenue': 0.0,
            'favorite_product_freq': 0,
            'repeat_product_ratio': 0.0,
            'customer_lifetime_days': 0,
            'purchase_rate': 0.0,
        }
        return empty