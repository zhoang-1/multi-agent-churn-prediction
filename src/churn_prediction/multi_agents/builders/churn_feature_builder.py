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
            customer_profile (dict): Phải chứa key "orders" là list các dict order.
        Returns:
            dict: Feature vector với các key đúng tên cột (26 feature số).
        """
        orders = customer_profile.get("orders", [])
        if not orders:
            return self._empty_features()

        df = pd.DataFrame(orders)

        # --- Chuẩn hóa tên cột ---
        # Ngày
        if 'InvoiceDate' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            date_col = 'InvoiceDate'
        elif 'order_date' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['order_date'])
            date_col = 'InvoiceDate'
        else:
            df['InvoiceDate'] = pd.Timestamp.now()
            date_col = 'InvoiceDate'

        # Mã hóa đơn
        if 'Invoice' in df.columns:
            invoice_col = 'Invoice'
        elif 'order_id' in df.columns:
            df['Invoice'] = df['order_id']
            invoice_col = 'Invoice'
        else:
            df['Invoice'] = df.index.astype(str)
            invoice_col = 'Invoice'

        # Mã sản phẩm
        if 'StockCode' in df.columns:
            product_col = 'StockCode'
        elif 'product_id' in df.columns:
            df['StockCode'] = df['product_id']
            product_col = 'StockCode'
        else:
            df['StockCode'] = 1
            product_col = 'StockCode'

        # Số lượng
        if 'Quantity' not in df.columns and 'num_items' in df.columns:
            df['Quantity'] = df['num_items']
        elif 'Quantity' not in df.columns:
            df['Quantity'] = 1

        # Đơn giá
        if 'Price' not in df.columns and 'unit_price' in df.columns:
            df['Price'] = df['unit_price']
        elif 'Price' not in df.columns:
            df['Price'] = 0

        # Doanh thu
        if 'Revenue' in df.columns:
            pass
        elif 'order_value' in df.columns:
            df['Revenue'] = df['order_value']
        else:
            df['Revenue'] = df['Quantity'] * df['Price']

        # --- Snapshot date ---
        if self.snapshot_date is None:
            snapshot = df[date_col].max() + pd.Timedelta(days=1)
        else:
            snapshot = pd.to_datetime(self.snapshot_date)

        # --- Tính toán các nhóm feature ---
        features = {}

        # 1. RFM
        features['Recency'] = (snapshot - df[date_col].max()).days
        features['Frequency'] = df[invoice_col].nunique()
        features['Monetary'] = df['Revenue'].sum()

        order_agg = df.groupby(invoice_col).agg(
            order_revenue=('Revenue', 'sum'),
            order_items=('Quantity', 'sum')
        ).reset_index()
        features['avg_order_value'] = order_agg['order_revenue'].mean() if len(order_agg) > 0 else 0.0
        features['avg_items_per_order'] = order_agg['order_items'].mean() if len(order_agg) > 0 else 0.0

        # 2. Purchase Behavior
        features['total_quantity'] = df['Quantity'].sum()
        features['total_orders'] = features['Frequency']
        unique_products = df[product_col].nunique()
        features['unique_products_x'] = unique_products
        features['unique_products_y'] = unique_products
        features['unique_purchase_days'] = df[date_col].dt.date.nunique()
        features['avg_quantity_per_order'] = (
            features['total_quantity'] / features['total_orders']
            if features['total_orders'] > 0 else 0.0
        )
        features['max_order_value'] = order_agg['order_revenue'].max() if len(order_agg) > 0 else 0.0
        features['min_order_value'] = order_agg['order_revenue'].min() if len(order_agg) > 0 else 0.0

        # 3. Time-based
        first_date = df[date_col].min()
        last_date = df[date_col].max()
        features['customer_age_days'] = (snapshot - first_date).days
        features['days_since_last_purchase'] = (snapshot - last_date).days
        features['purchase_span_days'] = (last_date - first_date).days

        unique_dates = df[date_col].sort_values().drop_duplicates()
        if len(unique_dates) >= 2:
            features['avg_days_between_orders'] = unique_dates.diff().dt.days.mean()
        else:
            features['avg_days_between_orders'] = 0.0

        # 4. Revenue
        features['total_revenue'] = features['Monetary']
        features['avg_revenue_per_item'] = (
            features['total_revenue'] / features['total_quantity']
            if features['total_quantity'] > 0 else 0.0
        )
        features['revenue_std'] = order_agg['order_revenue'].std() if len(order_agg) > 1 else 0.0
        features['max_revenue'] = features['max_order_value']

        cutoff_30d = snapshot - pd.Timedelta(days=30)
        recent_30d_df = df[df[date_col] >= cutoff_30d]
        features['recent_30d_revenue'] = recent_30d_df['Revenue'].sum() if not recent_30d_df.empty else 0.0

        # 5. Product Diversity (unique_products_x và unique_products_y đã có ở trên)
        product_counts = df.groupby(product_col).size()
        features['favorite_product_freq'] = product_counts.max() if len(product_counts) > 0 else 0
        features['repeat_product_ratio'] = (product_counts > 1).sum() / len(product_counts) if len(product_counts) > 0 else 0.0

        # 6. Loyalty (không trả về ngày tháng)
        features['customer_lifetime_days'] = (last_date - first_date).days
        if features['customer_lifetime_days'] > 0:
            features['purchase_rate'] = features['Frequency'] / features['customer_lifetime_days']
        else:
            features['purchase_rate'] = 0.0

        # Chuyển NaN -> 0 cho tất cả giá trị số
        for k, v in features.items():
            if isinstance(v, (pd.Timestamp, datetime)):
                continue
            if pd.isna(v):
                features[k] = 0.0

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