# agents/churn_agent.py
import joblib
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
logger = logging.getLogger(__name__)

class ChurnAgent:
    """
    Agent dự đoán rủi ro rời bỏ (churn) của khách hàng.

    Sử dụng model đã train sẵn (joblib) và các ngưỡng xác suất để phân loại mức rủi ro.

    Attributes:
        pipeline: Pipeline scikit-learn đã load.
        risk_thresholds (dict): Ngưỡng xác suất cho các mức rủi ro.
    """

    # Ngưỡng mặc định (có thể ghi đè qua constructor)
    DEFAULT_RISK_THRESHOLDS = {"high": 0.7, "medium": 0.4}

    def __init__(
        self,
        model_path: Union[str, Path],
        risk_thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        Khởi tạo ChurnAgent.

        Args:
            model_path (str | Path): Đường dẫn đến file model .joblib.
            risk_thresholds (dict, optional): Tùy chỉnh ngưỡng rủi ro.
                Ví dụ: {"high": 0.8, "medium": 0.5}
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model không tồn tại: {self.model_path}")

        try:
            self.pipeline = joblib.load(self.model_path)
            logger.info(f"Đã load model thành công từ {self.model_path}")
        except Exception as e:
            logger.error(f"Lỗi khi load model: {e}")
            raise

        # Thiết lập ngưỡng rủi ro
        self.risk_thresholds = risk_thresholds or self.DEFAULT_RISK_THRESHOLDS
        self._validate_thresholds()

    def _validate_thresholds(self) -> None:
        """Kiểm tra tính hợp lệ của các ngưỡng."""
        required = ["high", "medium"]
        for key in required:
            if key not in self.risk_thresholds:
                raise ValueError(f"Thiếu ngưỡng '{key}' trong risk_thresholds")
        if not (0 <= self.risk_thresholds["medium"] <= self.risk_thresholds["high"] <= 1):
            raise ValueError("Ngưỡng phải thỏa mãn: 0 <= medium <= high <= 1")

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dự đoán churn cho một khách hàng dựa trên các đặc trưng.

        Args:
            features (dict): Dict chứa các đặc trưng số.

        Returns:
            dict: Kết quả dự đoán gồm:
                - churn_probability (float): Xác suất rời bỏ.
                - churn_prediction (int): 0 hoặc 1.
                - risk_level (str): "high", "medium", hoặc "low".
                - error (str | None): Thông báo lỗi nếu có.
        """
        if not features:
            logger.warning("features rỗng")
            return {
                "churn_probability": None,
                "churn_prediction": None,
                "risk_level": None,
                "error": "Empty features",
            }

        try:
            # Chuyển features sang DataFrame
            X = pd.DataFrame([features])

            # Chỉ giữ các cột số (numeric) để tránh lỗi
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                error_msg = "Không có đặc trưng số nào"
                logger.error(error_msg)
                return {
                    "churn_probability": None,
                    "churn_prediction": None,
                    "risk_level": None,
                    "error": error_msg,
                }

            X = X[numeric_cols]

            # Dự đoán xác suất và nhãn
            churn_proba = float(self.pipeline.predict_proba(X)[0][1])
            churn_pred = int(self.pipeline.predict(X)[0])

            # Phân loại rủi ro theo ngưỡng
            high_th = self.risk_thresholds["high"]
            mid_th = self.risk_thresholds["medium"]

            if churn_proba >= high_th:
                risk = "high"
            elif churn_proba >= mid_th:
                risk = "medium"
            else:
                risk = "low"

            logger.debug(
                f"Dự đoán: prob={churn_proba:.4f}, pred={churn_pred}, risk={risk}"
            )

            return {
                "churn_probability": round(churn_proba, 4),
                "churn_prediction": churn_pred,
                "risk_level": risk,
                "error": None,
            }

        except Exception as e:
            error_msg = f"Lỗi khi dự đoán: {str(e)}"
            logger.error(error_msg)
            return {
                "churn_probability": None,
                "churn_prediction": None,
                "risk_level": None,
                "error": error_msg,
            }

    @classmethod
    def from_config(cls, config_path: Union[str, Path]):
        """
        Tạo agent từ file cấu hình JSON.

        Args:
            config_path (str | Path): Đường dẫn file config.

        Returns:
            ChurnAgent: Instance với cấu hình từ file.
        """
        import json

        config_path = Path(config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        model_path = config.get("model_path", "churn_prediction/churn_model.joblib")
        risk_thresholds = config.get("risk_thresholds", cls.DEFAULT_RISK_THRESHOLDS)

        return cls(model_path, risk_thresholds)