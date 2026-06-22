# agents/sentiment_agent.py
import joblib
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Optional, Union, Any
logger = logging.getLogger(__name__)

class SentimentAgent:
    """
    Agent phân tích cảm xúc (sentiment) cho văn bản đánh giá.

    Sử dụng model đã train sẵn (joblib) để dự đoán nhãn cảm xúc: positive, neutral, negative.

    Attributes:
        pipeline: Pipeline scikit-learn đã load (ví dụ: TF-IDF + classifier).
        label_map (dict): Ánh xạ từ chỉ số class sang tên nhãn.
    """

    # Label map mặc định (có thể ghi đè)
    DEFAULT_LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}

    def __init__(
        self,
        model_path: Union[str, Path],
        label_map: Optional[Dict[int, str]] = None,
    ):
        """
        Khởi tạo SentimentAgent.

        Args:
            model_path (str | Path): Đường dẫn đến file model .joblib.
            label_map (dict, optional): Ánh xạ chỉ số -> tên nhãn.
                Mặc định: {0: "negative", 1: "neutral", 2: "positive"}
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

        # Thiết lập label_map
        if label_map is not None:
            # Chuyển đổi key sang int nếu cần
            self.label_map = {int(k): v for k, v in label_map.items()}
        else:
            self.label_map = self.DEFAULT_LABEL_MAP.copy()

        self._validate_label_map()

    def _validate_label_map(self) -> None:
        """Kiểm tra label_map có hợp lệ không."""
        if not self.label_map:
            raise ValueError("label_map không được rỗng")
        # Kiểm tra các chỉ số có liên tục không (không bắt buộc)
        for idx in self.label_map.keys():
            if not isinstance(idx, int) or idx < 0:
                raise ValueError(f"Chỉ số class phải là số nguyên không âm: {idx}")

    def analyze(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phân tích cảm xúc dựa trên đặc trưng số học.

        Args:
            features (dict): Dict chứa các đặc trưng số từ SentimentFeatureBuilder.

        Returns:
            dict: Kết quả phân tích gồm:
                - label (str): "positive", "neutral", "negative", "unknown", hoặc "error".
                - confidence (float): Độ tin cậy của dự đoán (xác suất max).
                - proba (dict): Xác suất cho từng nhãn.
                - error (str | None): Thông báo lỗi nếu có.
        """
        if not features:
            logger.warning("Features rỗng")
            return {
                "label": "unknown",
                "confidence": 0.0,
                "proba": {},
                "error": "Empty features",
            }

        try:
            import pandas as pd
            # Chuyển features sang DataFrame
            X = pd.DataFrame([features])

            # Chỉ giữ các cột số (numeric) để tránh lỗi
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                error_msg = "Không có đặc trưng số nào"
                logger.error(error_msg)
                return {
                    "label": "unknown",
                    "confidence": 0.0,
                    "proba": {},
                    "error": error_msg,
                }

            X = X[numeric_cols]
            proba = self.pipeline.predict_proba(X)[0]
            label_idx = int(np.argmax(proba))
            confidence = float(proba[label_idx])

            label = self.label_map.get(label_idx, str(label_idx))

            # Tạo dict xác suất cho tất cả nhãn
            proba_dict = {
                self.label_map.get(i, str(i)): round(float(p), 4)
                for i, p in enumerate(proba)
            }

            logger.debug(f"Phân tích hoàn tất: label={label}, conf={confidence:.4f}")

            return {
                "label": label,
                "confidence": round(confidence, 4),
                "proba": proba_dict,
                "error": None,
            }

        except Exception as e:
            error_msg = f"Lỗi khi phân tích: {str(e)}"
            logger.error(error_msg)
            return {
                "label": "error",
                "confidence": 0.0,
                "proba": {},
                "error": error_msg,
            }

    @classmethod
    def from_config(cls, config_path: Union[str, Path]):
        """
        Tạo agent từ file cấu hình JSON.

        Args:
            config_path (str | Path): Đường dẫn file config.

        Returns:
            SentimentAgent: Instance với cấu hình từ file.
        """
        import json

        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"File config không tồn tại: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        model_path = config.get("model_path", "churn_prediction/sentiment_model.joblib")
        label_map_raw = config.get("label_map", None)

        # Chuyển đổi label_map từ dict có key là string sang int
        label_map = None
        if label_map_raw:
            label_map = {int(k): v for k, v in label_map_raw.items()}

        return cls(model_path, label_map)