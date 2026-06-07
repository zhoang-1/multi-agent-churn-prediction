import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from churn_prediction.paths import MODELS_DIR

class ModelTrainer:
    """Huấn luyện và tối ưu nhiều mô hình, lưu model tốt nhất"""
    
    def __init__(self):
        self.best_model = None
        self.best_score = 0
        self.models = {
            "XGBoost": XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
            "LightGBM": LGBMClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42)
        }
    
    def train_and_evaluate(self, X, y, test_size=0.2):
        """Chia train/test, huấn luyện, đánh giá, chọn model tốt nhất"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, stratify=y, random_state=42
        )
        results = {}
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
            results[name] = {"model": model, "auc": auc}
            print(f"{name}: AUC = {auc:.4f}")
            if auc > self.best_score:
                self.best_score = auc
                self.best_model = model
        # Lưu model tốt nhất
        with open(MODELS_DIR / "best_churn_model.pkl", "wb") as f:
            pickle.dump(self.best_model, f)
        return results

    def hyperparameter_tuning(self, X, y, model_name="XGBoost"):
        """Tinh chỉnh hyperparameter với GridSearchCV (tùy chọn)"""
        param_grid = {
            "XGBoost": {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2]
            }
        }.get(model_name, {})
        if not param_grid:
            return None
        gs = GridSearchCV(self.models[model_name], param_grid, cv=5, scoring='roc_auc')
        gs.fit(X, y)
        return gs.best_estimator_