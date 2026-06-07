import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from churn_prediction.paths import REPORTS_DIR

class EDATool:
    """Thực hiện EDA và trả về báo cáo chất lượng dữ liệu"""
    
    @staticmethod
    def analyze_data(df: pd.DataFrame) -> dict:
        """Phân tích dữ liệu: missing, duplicates, outliers, class balance"""
        report = {
            "shape": df.shape,
            "missing": df.isnull().sum().to_dict(),
            "duplicates": df.duplicated().sum(),
            "class_balance": None
        }
        if "is_churned" in df.columns:
            report["class_balance"] = df["is_churned"].value_counts().to_dict()
        # Phát hiện outlier bằng IQR
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers = {}
        for col in numeric_cols:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            outliers[col] = ((df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)).sum()
        report["outliers"] = outliers
        return report

    @staticmethod
    def plot_class_distribution(df: pd.DataFrame, target_col: str = "is_churned"):
        """Vẽ biểu đồ phân phối nhãn và lưu vào reports/figures/"""
        plt.figure(figsize=(6,4))
        df[target_col].value_counts().plot(kind='bar', color=['#2ed573', '#ff6b6b'])
        plt.title("Class Distribution (Churn vs Non-Churn)")
        plt.xlabel("Churn Status")
        plt.ylabel("Count")
        plt.savefig(REPORTS_DIR / "figures" / "class_distribution.png")
        plt.close()