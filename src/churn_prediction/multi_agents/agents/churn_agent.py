# agents/churn_agent.py
import joblib
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from churn_prediction.paths import CHURN_MODEL_PATH

logger = logging.getLogger(__name__)

class ChurnAgent:
    """
    Agent dự đoán rủi ro rời bỏ (churn) của khách hàng.
    """

    DEFAULT_RISK_THRESHOLDS = {"high": 0.7, "medium": 0.4}

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        risk_thresholds: Optional[Dict[str, float]] = None,
    ):
        if model_path is None:
            model_path = CHURN_MODEL_PATH
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model không tồn tại: {self.model_path}")

        try:
            self.pipeline = joblib.load(self.model_path)
            logger.info(f"Đã load model thành công từ {self.model_path}")
            # Lưu danh sách tên cột nếu có
            if hasattr(self.pipeline, 'feature_names_in_'):
                self.feature_names = list(self.pipeline.feature_names_in_)
                logger.info(f"Feature names từ model: {self.feature_names}")
            else:
                self.feature_names = None
                logger.warning("Model không có feature_names_in_, sẽ dùng sorted keys")
        except Exception as e:
            logger.error(f"Lỗi khi load model: {e}")
            raise

        self.risk_thresholds = risk_thresholds or self.DEFAULT_RISK_THRESHOLDS
        self._validate_thresholds()

    def _validate_thresholds(self) -> None:
        required = ["high", "medium"]
        for key in required:
            if key not in self.risk_thresholds:
                raise ValueError(f"Thiếu ngưỡng '{key}' trong risk_thresholds")
        if not (0 <= self.risk_thresholds["medium"] <= self.risk_thresholds["high"] <= 1):
            raise ValueError("Ngưỡng phải thỏa mãn: 0 <= medium <= high <= 1")

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not features:
            return {
                "churn_probability": None,
                "churn_prediction": None,
                "risk_level": None,
                "error": "Empty features",
            }

        try:
            # Xác định danh sách cột theo đúng thứ tự
            if self.feature_names is not None:
                feature_names = self.feature_names
            else:
                # Fallback: sắp xếp theo alphabet
                feature_names = sorted(features.keys())
                # Cảnh báo rằng thứ tự có thể không đúng
                logger.warning("Sử dụng thứ tự sắp xếp alphabet, có thể gây sai nếu model yêu cầu thứ tự cố định")

            # Đảm bảo features có tất cả các cột cần thiết
            # Nếu thiếu, thêm với giá trị 0
            for col in feature_names:
                if col not in features:
                    logger.warning(f"Thiếu feature '{col}', đặt giá trị 0")
                    features[col] = 0.0

            # Tạo DataFrame với các cột đúng thứ tự
            X = pd.DataFrame([features])[feature_names]

            # Chuyển sang kiểu số (float)
            X = X.astype(float)

            churn_proba = float(self.pipeline.predict_proba(X)[0][1])
            churn_pred = int(self.pipeline.predict(X)[0])

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
        import json
        config_path = Path(config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        model_path = config.get("model_path", CHURN_MODEL_PATH)
        risk_thresholds = config.get("risk_thresholds", cls.DEFAULT_RISK_THRESHOLDS)

        return cls(model_path, risk_thresholds)