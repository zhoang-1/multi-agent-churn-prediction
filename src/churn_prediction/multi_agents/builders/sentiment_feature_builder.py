import numpy as np
import pandas as pd
from datetime import datetime

class SentimentFeatureBuilder:
    """
    Builds exactly 30 features for customer experience modeling.
    Features match the selection in modeling_pipeline.ipynb.
    """

    # Fixed list of 30 feature names
    FEATURE_NAMES = [
        'recency', 'frequency', 'monetary', 'rfm_segment',
        'avg_delivery_time', 'std_delivery_time', 'max_delivery_time',
        'avg_estimated_delivery', 'avg_freight_per_order',
        'num_comments', 'num_titles', 'avg_days_to_answer',
        'avg_items_per_order', 'night_purchase_ratio', 'total_orders',
        'avg_gap', 'max_gap', 'avg_installments', 'favorite_payment_type',
        'credit_card_ratio', 'boleto_ratio', 'spending_trend', 'order_trend',
        'recent_vs_old_ratio', 'avg_order_trend', 'total_comments_msg',
        'total_comments_title', 'unique_sellers', 'customer_state',
        'num_categories_bought'
    ]

    def build(self, customer_profile):
        """
        Build đúng 30 feature từ customer_profile theo cấu trúc MongoDB.
        """

        # =====================================================
        # Default values
        # =====================================================
        features = {name: 0 for name in self.FEATURE_NAMES}
        features["rfm_segment"] = "unknown"
        features["favorite_payment_type"] = "unknown"
        features["customer_state"] = "unknown"

        orders = customer_profile.get("orders", [])

        if not orders:
            return features

        rows = []

        for order in orders:

            payment = order.get("payment", {})
            delivery = order.get("delivery", {})
            review = order.get("review", {})
            items = order.get("items", [])

            purchase_date = pd.to_datetime(
                order.get("order_date"),
                errors="coerce"
            )

            delivered_date = pd.to_datetime(
                delivery.get("delivered_date"),
                errors="coerce"
            )

            estimated_days = delivery.get("estimated_days", 0)
            actual_days = delivery.get("actual_days", 0)

            # Nếu không có item vẫn tạo 1 record
            if not items:
                items = [{}]

            seller_ids = []
            product_categories = []

            total_products = 0

            for item in items:

                seller = item.get("seller_id")
                if seller:
                    seller_ids.append(seller)

                category = item.get("category")
                if category:
                    product_categories.append(category)

                total_products += item.get("quantity", 0)

            rows.append({

                # ==========================
                # Order
                # ==========================
                "order_purchase_timestamp": purchase_date,

                "order_delivered_customer_date": delivered_date,

                "order_estimated_delivery_date":
                    purchase_date + pd.Timedelta(days=estimated_days)
                    if pd.notna(purchase_date)
                    else pd.NaT,

                "delivery_time_days": actual_days,

                "estimated_delivery_days": estimated_days,

                # ==========================
                # Payment
                # ==========================
                "payment_type": payment.get("method", "unknown"),

                "payment_installments":
                    payment.get("installments", 1),

                "total_payment":
                    payment.get("total_payment", 0),

                # ==========================
                # Freight
                # ==========================
                "avg_freight":
                    delivery.get("freight_value", 0),

                # ==========================
                # Review
                # ==========================
                "days_to_answer":
                    review.get("answer_time_days", 0),

                "num_comment_messages":
                    1 if review.get("comment") else 0,

                "num_comment_titles":
                    1 if review.get("score") is not None else 0,

                # ==========================
                # Items
                # ==========================
                "num_products": total_products,

                "seller_ids": seller_ids,

                "product_categories": product_categories,

                # ==========================
                # Customer
                # ==========================
                "customer_state":
                    customer_profile.get("customer", {})
                    .get("address", {})
                    .get("state", "unknown")
            })

        df = pd.DataFrame(rows)

        if df.empty:
            return features

        # =====================================================
        # Convert datetime
        # =====================================================

        for col in [
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]:
            if col in df.columns:
                df[col] = pd.to_datetime(
                    df[col],
                    errors="coerce"
                )

        # =====================================================
        # Numeric columns
        # =====================================================

        numeric_cols = [
            "delivery_time_days",
            "estimated_delivery_days",
            "payment_installments",
            "total_payment",
            "avg_freight",
            "days_to_answer",
            "num_comment_messages",
            "num_comment_titles",
            "num_products"
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = (
                    pd.to_numeric(df[col], errors="coerce")
                    .fillna(0)
                )

        # =====================================================
        # Build features
        # =====================================================

        features.update(self._build_rfm(df))
        features.update(self._build_delivery(df))
        features.update(self._build_payment(df))
        features.update(self._build_review(df))
        features.update(self._build_trend(df))
        features.update(self._build_behavior(df))

        # =====================================================
        # Clean NaN
        # =====================================================

        for key in self.FEATURE_NAMES:

            if key not in features:
                features[key] = (
                    "unknown"
                    if key in [
                        "rfm_segment",
                        "favorite_payment_type",
                        "customer_state"
                    ]
                    else 0
                )

            if pd.isna(features[key]):
                features[key] = (
                    "unknown"
                    if key in [
                        "rfm_segment",
                        "favorite_payment_type",
                        "customer_state"
                    ]
                    else 0
                )

            if isinstance(features[key], np.generic):
                features[key] = features[key].item()

        return features
    # ------------------------------------------------------------------
    # Các thành phần con – mỗi thành phần trả về chính xác các khóa cho nhóm của nó.
    # ------------------------------------------------------------------

    def _build_rfm(self, df):
        last_order = df['order_purchase_timestamp'].max()
        recency = (pd.Timestamp.now() - last_order).days
        frequency = len(df)
        monetary = df.get('total_payment', df.get('order_value', 0)).sum()

        # Segment logic (same as in feature_engineering.ipynb)
        recency_score = 4 if recency <= 30 else (3 if recency <= 90 else (2 if recency <= 180 else 1))
        frequency_score = 4 if frequency >= 5 else (3 if frequency >= 3 else (2 if frequency >= 2 else 1))
        monetary_score = 4 if monetary >= 500 else (3 if monetary >= 200 else (2 if monetary >= 100 else 1))

        if recency_score >= 3 and frequency_score >= 3 and monetary_score >= 3:
            segment = 'champion'
        elif recency_score >= 3 and frequency_score >= 2:
            segment = 'loyal'
        elif recency_score <= 2 and frequency_score <= 2 and monetary_score <= 2:
            segment = 'at_risk'
        elif recency_score <= 1:
            segment = 'churned'
        else:
            segment = 'promising'

        return {
            "recency": recency,
            "frequency": frequency,
            "monetary": monetary,
            "rfm_segment": segment
        }

    def _build_delivery(self, df):
        # Delivery times
        if 'delivery_time_days' in df.columns:
            avg_del = df['delivery_time_days'].mean()
            std_del = df['delivery_time_days'].std()
            max_del = df['delivery_time_days'].max()
        else:
            avg_del = std_del = max_del = 0

        # Estimated delivery
        if 'estimated_delivery_days' in df.columns:
            avg_est = df['estimated_delivery_days'].mean()
        else:
            avg_est = 0

        # Freight
        if 'avg_freight' in df.columns:
            avg_freight = df['avg_freight'].mean()
        elif 'total_freight' in df.columns and 'num_products' in df.columns:
            avg_freight = (df['total_freight'] / df['num_products']).mean()
        else:
            avg_freight = 0

        return {
            "avg_delivery_time": avg_del,
            "std_delivery_time": std_del,
            "max_delivery_time": max_del,
            "avg_estimated_delivery": avg_est,
            "avg_freight_per_order": avg_freight
        }

    def _build_payment(self, df):
        # Installments
        if 'max_installments' in df.columns:
            avg_install = df['max_installments'].mean()
        elif 'payment_installments' in df.columns:
            avg_install = df['payment_installments'].mean()
        else:
            avg_install = 1

        # Payment type
        payment_col = None
        if 'main_payment_type' in df.columns:
            payment_col = 'main_payment_type'
        elif 'payment_type' in df.columns:
            payment_col = 'payment_type'

        if payment_col:
            credit_ratio = (df[payment_col] == 'credit_card').mean()
            boleto_ratio = (df[payment_col] == 'boleto').mean()
            mode_val = df[payment_col].mode()
            favorite = mode_val[0] if not mode_val.empty else 'unknown'
        else:
            credit_ratio = 0
            boleto_ratio = 0
            favorite = 'unknown'

        return {
            "avg_installments": avg_install,
            "credit_card_ratio": credit_ratio,
            "boleto_ratio": boleto_ratio,
            "favorite_payment_type": favorite
        }

    def _build_review(self, df):
        # Days to answer
        if 'days_to_answer' in df.columns:
            avg_days = df['days_to_answer'].mean()
        else:
            avg_days = 0

        # Comment counts and totals
        if 'num_comment_messages' in df.columns:
            num_comments = df['num_comment_messages'].notna().sum()
            total_msg = df['num_comment_messages'].sum()
        else:
            num_comments = 0
            total_msg = 0

        if 'num_comment_titles' in df.columns:
            num_titles = df['num_comment_titles'].notna().sum()
            total_title = df['num_comment_titles'].sum()
        else:
            num_titles = 0
            total_title = 0

        return {
            "num_comments": num_comments,
            "num_titles": num_titles,
            "avg_days_to_answer": avg_days,
            "total_comments_msg": total_msg,
            "total_comments_title": total_title
        }

    def _build_trend(self, df):
        # Sắp xếp theo thời gian
        if 'order_purchase_timestamp' in df.columns:
            df_sorted = df.sort_values('order_purchase_timestamp')
        else:
            df_sorted = df

        n = len(df_sorted)
        if n < 3:
            return {
                "spending_trend": 0,
                "order_trend": 0,
                "recent_vs_old_ratio": 0,
                "avg_order_trend": 0
            }

        half = n // 2
        old = df_sorted.head(half)
        recent = df_sorted.tail(half)

        payment_col = 'total_payment' if 'total_payment' in df_sorted.columns else ('order_value' if 'order_value' in df_sorted.columns else None)

        if payment_col:
            old_spend = old[payment_col].mean()
            recent_spend = recent[payment_col].mean()
            spending_trend = (recent_spend - old_spend) / (old_spend + 1)
            old_avg = old[payment_col].sum() / len(old)
            recent_avg = recent[payment_col].sum() / len(recent)
            avg_order_trend = (recent_avg - old_avg) / (old_avg + 1)
        else:
            spending_trend = 0
            avg_order_trend = 0

        order_trend = (len(recent) - len(old)) / (len(old) + 1)
        recent_vs_old_ratio = len(recent) / (len(old) + 1)

        return {
            "spending_trend": spending_trend,
            "order_trend": order_trend,
            "recent_vs_old_ratio": recent_vs_old_ratio,
            "avg_order_trend": avg_order_trend
        }

    def _build_behavior(self, df):
        # Items per order
        if 'num_products' in df.columns:
            avg_items = df['num_products'].mean()
        else:
            avg_items = 0

        # Total orders
        total_orders = len(df)

        # Night purchase ratio
        if 'order_purchase_timestamp' in df.columns:
            purchase_hour = df['order_purchase_timestamp'].dt.hour
            night_ratio = purchase_hour.isin(range(20, 24)).mean()
        else:
            night_ratio = 0

        # Gaps between orders
        if 'order_purchase_timestamp' in df.columns and len(df) >= 2:
            sorted_dates = df['order_purchase_timestamp'].sort_values()
            gaps = sorted_dates.diff().dt.days.dropna()
            avg_gap = gaps.mean() if len(gaps) > 0 else 0
            max_gap = gaps.max() if len(gaps) > 0 else 0
        else:
            avg_gap = 0
            max_gap = 0

        # Unique sellers
        if 'seller_id' in df.columns:
            unique_sellers = df['seller_id'].nunique()
        elif 'seller_ids' in df.columns:
            all_sellers = set()
            for ids in df['seller_ids']:
                if isinstance(ids, list):
                    all_sellers.update(ids)
            unique_sellers = len(all_sellers)
        else:
            unique_sellers = 0

        # Customer state
        if 'customer_state' in df.columns:
            mode_state = df['customer_state'].mode()
            customer_state = mode_state[0] if not mode_state.empty else 'unknown'
        else:
            customer_state = 'unknown'

        # Number of product categories
        if 'product_category' in df.columns:
            num_cats = df['product_category'].nunique()
        elif 'product_categories' in df.columns:
            all_cats = set()
            for cats in df['product_categories']:
                if isinstance(cats, list):
                    all_cats.update(cats)
            num_cats = len(all_cats)
        else:
            num_cats = 0

        return {
            "avg_items_per_order": avg_items,
            "night_purchase_ratio": night_ratio,
            "total_orders": total_orders,
            "avg_gap": avg_gap,
            "max_gap": max_gap,
            "unique_sellers": unique_sellers,
            "customer_state": customer_state,
            "num_categories_bought": num_cats
        }