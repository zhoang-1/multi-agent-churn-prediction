import numpy as np
import pandas as pd
from datetime import datetime

class SentimentFeatureBuilder:

    def build(self, customer_profile):
        orders = customer_profile.get("orders", [])
        
        if not orders:
            return self._empty_features()

        df = pd.DataFrame(orders)
        
        # Ensure timestamp types if needed
        if 'order_purchase_timestamp' in df.columns:
            df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        else:
            # Fallback if no timestamp
            df['order_purchase_timestamp'] = pd.Timestamp.now()
            
        features = {}
        features.update(self._build_rfm(df))
        features.update(self._build_delivery(df))
        features.update(self._build_payment(df))
        features.update(self._build_review(df))
        features.update(self._build_trend(df))
        features.update(self._build_behavior(df))

        # Gán unknown/0 cho các feature NaN
        for k, v in features.items():
            if pd.isna(v):
                features[k] = 0

        return features

    def _empty_features(self):
        return {
            "recency": 0, "frequency": 0, "monetary": 0,
            "avg_delivery_time": 0, "std_delivery_time": 0, "max_delivery_time": 0,
            "avg_estimated_delivery": 0, "avg_delivery_delay": 0, "late_delivery_ratio": 0,
            "avg_freight_per_order": 0,
            "avg_installments": 0, "credit_card_ratio": 0, "boleto_ratio": 0,
            "avg_review_score": 0, "std_review_score": 0, "min_review_score": 0,
            "num_bad_reviews": 0, "low_review_ratio": 0, "avg_days_to_answer": 0,
            "spending_trend": 0, "order_trend": 0, "recent_vs_old_ratio": 0,
            "avg_items_per_order": 0, "weekend_purchase_ratio": 0, "night_purchase_ratio": 0
        }

    def _build_rfm(self, df):
        if 'order_purchase_timestamp' not in df.columns or 'total_payment' not in df.columns:
            # Fallback based on old 'order_value' if present
            order_val_col = 'total_payment' if 'total_payment' in df.columns else 'order_value'
            val = df[order_val_col].sum() if order_val_col in df.columns else 0
            
            if 'order_date' in df.columns:
                last_order_date = pd.to_datetime(df["order_date"]).max()
                recency = (pd.Timestamp.now() - last_order_date).days
            elif 'order_purchase_timestamp' in df.columns:
                last_order_date = df["order_purchase_timestamp"].max()
                recency = (pd.Timestamp.now() - last_order_date).days
            else:
                recency = 0
                
            return {
                "recency": recency,
                "frequency": len(df),
                "monetary": val
            }

        last_order_date = df["order_purchase_timestamp"].max()
        recency = (pd.Timestamp.now() - last_order_date).days
        frequency = len(df)
        monetary = df["total_payment"].sum()

        return {
            "recency": recency,
            "frequency": frequency,
            "monetary": monetary
        }

    def _build_delivery(self, df):
        features = {}
        
        if 'delivery_time_days' in df.columns:
            features['avg_delivery_time'] = df['delivery_time_days'].mean()
            features['std_delivery_time'] = df['delivery_time_days'].std()
            features['max_delivery_time'] = df['delivery_time_days'].max()
        elif 'order_delivered_customer_date' in df.columns and 'order_purchase_timestamp' in df.columns:
            delivery_time = (pd.to_datetime(df['order_delivered_customer_date']) - df['order_purchase_timestamp']).dt.days
            features['avg_delivery_time'] = delivery_time.mean()
            features['std_delivery_time'] = delivery_time.std()
            features['max_delivery_time'] = delivery_time.max()
        else:
            features['avg_delivery_time'] = 0
            features['std_delivery_time'] = 0
            features['max_delivery_time'] = 0

        if 'delivery_delay' in df.columns:
            features['avg_delivery_delay'] = df['delivery_delay'].mean()
            features['late_delivery_ratio'] = (df['delivery_delay'] > 0).mean()
        elif 'order_estimated_delivery_date' in df.columns and 'order_delivered_customer_date' in df.columns:
            est_time = (pd.to_datetime(df['order_estimated_delivery_date']) - df['order_purchase_timestamp']).dt.days
            delivery_time = (pd.to_datetime(df['order_delivered_customer_date']) - df['order_purchase_timestamp']).dt.days
            delay = delivery_time - est_time
            features['avg_delivery_delay'] = delay.mean()
            features['late_delivery_ratio'] = (delay > 0).mean()
        else:
            features['avg_delivery_delay'] = 0
            features['late_delivery_ratio'] = 0

        if 'avg_freight' in df.columns:
            features['avg_freight_per_order'] = df['avg_freight'].mean()
        else:
            features['avg_freight_per_order'] = 0
            
        return features

    def _build_payment(self, df):
        features = {}
        if 'max_installments' in df.columns:
            features['avg_installments'] = df['max_installments'].mean()
        elif 'payment_installments' in df.columns:
            features['avg_installments'] = df['payment_installments'].mean()
        else:
            features['avg_installments'] = 1

        if 'main_payment_type' in df.columns:
            features['credit_card_ratio'] = (df['main_payment_type'] == 'credit_card').mean()
            features['boleto_ratio'] = (df['main_payment_type'] == 'boleto').mean()
        elif 'payment_type' in df.columns:
            features['credit_card_ratio'] = (df['payment_type'] == 'credit_card').mean()
            features['boleto_ratio'] = (df['payment_type'] == 'boleto').mean()
        else:
            features['credit_card_ratio'] = 0
            features['boleto_ratio'] = 0
            
        return features

    def _build_review(self, df):
        features = {}
        if 'review_score' in df.columns:
            features['avg_review_score'] = df['review_score'].mean()
            features['std_review_score'] = df['review_score'].std()
            features['min_review_score'] = df['review_score'].min()
            features['low_review_ratio'] = (df['review_score'] <= 2).mean()
            features['num_bad_reviews'] = (df['review_score'] <= 2).sum()
        else:
            features['avg_review_score'] = 0
            features['std_review_score'] = 0
            features['min_review_score'] = 0
            features['low_review_ratio'] = 0
            features['num_bad_reviews'] = 0
            
        if 'days_to_answer' in df.columns:
            features['avg_days_to_answer'] = df['days_to_answer'].mean()
        else:
            features['avg_days_to_answer'] = 0

        return features

    def _build_trend(self, df):
        features = {}
        if len(df) < 3:
            return {"spending_trend": 0, "order_trend": 0, "recent_vs_old_ratio": 0}
            
        # Sắp xếp lại theo thời gian
        df_sorted = df.sort_values('order_purchase_timestamp') if 'order_purchase_timestamp' in df.columns else df
        
        half = len(df_sorted) // 2
        old = df_sorted.head(half)
        recent = df_sorted.tail(half)
        
        payment_col = 'total_payment' if 'total_payment' in df_sorted.columns else ('order_value' if 'order_value' in df_sorted.columns else None)
        
        if payment_col:
            old_spend = old[payment_col].mean()
            recent_spend = recent[payment_col].mean()
            features['spending_trend'] = (recent_spend - old_spend) / (old_spend + 1)
        else:
            features['spending_trend'] = 0
            
        features['order_trend'] = (len(recent) - len(old)) / (len(old) + 1)
        features['recent_vs_old_ratio'] = len(recent) / (len(old) + 1)
        
        return features

    def _build_behavior(self, df):
        features = {}
        if 'num_products' in df.columns:
            features['avg_items_per_order'] = df['num_products'].mean()
        else:
            features['avg_items_per_order'] = 0
            
        if 'order_purchase_timestamp' in df.columns:
            purchase_hour = df['order_purchase_timestamp'].dt.hour
            purchase_weekday = df['order_purchase_timestamp'].dt.dayofweek
            features['weekend_purchase_ratio'] = purchase_weekday.isin([5,6]).mean()
            features['night_purchase_ratio'] = purchase_hour.isin(range(20,24)).mean()
        else:
            features['weekend_purchase_ratio'] = 0
            features['night_purchase_ratio'] = 0
            
        return features