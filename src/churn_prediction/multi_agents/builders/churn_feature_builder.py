import pandas as pd
from datetime import datetime

class ChurnFeatureBuilder:

    def build(self, customer_profile: dict):
        orders = customer_profile.get("orders", [])

        if not orders:
            return self._empty_features()

        df = pd.DataFrame(orders)

        # Standardize date columns
        if 'InvoiceDate' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            date_col = 'InvoiceDate'
        elif 'order_date' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['order_date'])
            date_col = 'InvoiceDate'
        else:
            df['InvoiceDate'] = pd.Timestamp.now()
            date_col = 'InvoiceDate'

        # Standardize Revenue/Monetary
        if 'Revenue' in df.columns:
            revenue_col = 'Revenue'
        elif 'order_value' in df.columns:
            revenue_col = 'order_value'
            df['Revenue'] = df['order_value']
        else:
            if 'Quantity' in df.columns and 'Price' in df.columns:
                df['Revenue'] = df['Quantity'] * df['Price']
            else:
                df['Revenue'] = 0
            revenue_col = 'Revenue'

        # Standardize quantity
        if 'Quantity' not in df.columns and 'num_items' in df.columns:
            df['Quantity'] = df['num_items']
        elif 'Quantity' not in df.columns:
            df['Quantity'] = 1
            
        # Standardize Invoice/Order ID
        if 'Invoice' not in df.columns and 'order_id' in df.columns:
            df['Invoice'] = df['order_id']
        elif 'Invoice' not in df.columns:
            df['Invoice'] = df.index # Dummy

        snapshot_date = df[date_col].max() + pd.Timedelta(days=1)
        
        features = {}
        
        # 1. RFM
        features['recency'] = (snapshot_date - df[date_col].max()).days
        features['frequency'] = df['Invoice'].nunique()
        features['monetary'] = df['Revenue'].sum()
        
        order_agg = df.groupby('Invoice').agg({
            'Revenue': 'sum',
            'Quantity': 'sum'
        })
        features['avg_order_value'] = order_agg['Revenue'].mean()
        features['avg_items_per_order'] = order_agg['Quantity'].mean()

        # 2. Purchase Behavior
        features['total_quantity'] = df['Quantity'].sum()
        features['total_orders'] = features['frequency']
        features['unique_products'] = df['StockCode'].nunique() if 'StockCode' in df.columns else (df['product_id'].nunique() if 'product_id' in df.columns else 1)
        features['unique_purchase_days'] = df[date_col].dt.date.nunique()
        features['avg_quantity_per_order'] = features['total_quantity'] / features['total_orders'] if features['total_orders'] > 0 else 0
        features['max_order_value'] = order_agg['Revenue'].max()
        features['min_order_value'] = order_agg['Revenue'].min()

        # 3. Time-based
        first_date = df[date_col].min()
        last_date = df[date_col].max()
        features['customer_age_days'] = (snapshot_date - first_date).days
        features['days_since_last_purchase'] = (snapshot_date - last_date).days
        features['purchase_span_days'] = (last_date - first_date).days
        
        unique_dates = df[date_col].sort_values().drop_duplicates()
        if len(unique_dates) >= 2:
            features['avg_days_between_orders'] = unique_dates.diff().dt.days.mean()
        else:
            features['avg_days_between_orders'] = 0

        # 4. Revenue
        features['total_revenue'] = features['monetary']
        features['avg_revenue_per_item'] = features['total_revenue'] / features['total_quantity'] if features['total_quantity'] > 0 else 0
        features['revenue_std'] = order_agg['Revenue'].std() if len(order_agg) > 1 else 0
        features['max_revenue'] = features['max_order_value']
        
        cutoff_30d = snapshot_date - pd.Timedelta(days=30)
        recent_30d_df = df[df[date_col] >= cutoff_30d]
        features['recent_30d_revenue'] = recent_30d_df['Revenue'].sum() if not recent_30d_df.empty else 0

        # Fill NaNs
        for k, v in features.items():
            if pd.isna(v):
                features[k] = 0

        return features

    def _empty_features(self):
        return {
            "recency": 0, "frequency": 0, "monetary": 0, "avg_order_value": 0, "avg_items_per_order": 0,
            "total_quantity": 0, "total_orders": 0, "unique_products": 0, "unique_purchase_days": 0,
            "avg_quantity_per_order": 0, "max_order_value": 0, "min_order_value": 0,
            "customer_age_days": 0, "days_since_last_purchase": 0, "purchase_span_days": 0, "avg_days_between_orders": 0,
            "total_revenue": 0, "avg_revenue_per_item": 0, "revenue_std": 0, "max_revenue": 0, "recent_30d_revenue": 0
        }