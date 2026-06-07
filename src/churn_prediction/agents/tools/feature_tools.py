import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_selection import mutual_info_classif, SelectKBest
from imblearn.over_sampling import SMOTE
from churn_prediction.paths import MODELS_DIR
import pickle

class FeatureProcessor:
    """Xử lý đặc trưng: encoding, scaling, SMOTE, lựa chọn và lưu transformer"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoders = {}
        self.selected_features = None
    
    def process(self, df: pd.DataFrame, target_col: str = "is_churned", 
                categorical_cols: list = None, apply_smote: bool = True):
        """Thực hiện encoding, scaling, optional SMOTE"""
        X = df.drop(columns=[target_col])
        y = df[target_col]
        # Label encoding
        if categorical_cols is None:
            categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.encoders[col] = le
        # Scaling
        X_scaled = self.scaler.fit_transform(X)
        if apply_smote:
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X_scaled, y)
        else:
            X_resampled, y_resampled = X_scaled, y
        # Lưu scaler và encoders
        with open(MODELS_DIR / 'scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        with open(MODELS_DIR / 'label_encoders.pkl', 'wb') as f:
            pickle.dump(self.encoders, f)
        return X_resampled, y_resampled
    def select_features(self, X: pd.DataFrame, y: pd.Series, k: int = 10):
        """ Lựa chon các đặc trưng quan trọng nhất trong 51 đặc trưng bằng mutual information và lưu tên đặc trưng đã chọn"""
        selector = SelectKBest(mutual_info_classif, k=k)
        selector.fit(X, y)
        self.selected_features = X.columns[selector.get_support()].tolist()
        with open(MODELS_DIR / 'selected_features.pkl', 'wb') as f:
            pickle.dump(self.selected_features, f)
        return self.selected_features
    def transform(self, df: pd.DataFrame):
        """Áp dụng các transformer đã lưu để biến đổi dữ liệu mới"""
        # Apply label encoding
        for col, le in self.encoders.items():
            if col in df.columns:
                df[col] = le.transform(df[col].astype(str))
                        