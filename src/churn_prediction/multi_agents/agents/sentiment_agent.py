# agents/sentiment_agent.py
import joblib
import numpy as np
import logging
import pickle
from pathlib import Path
from typing import Dict, Optional, Union, Any, List

# Import đường dẫn model từ paths
from churn_prediction.paths import SENTIMENT_MODEL_PATH

logger = logging.getLogger(__name__)

class SentimentAgent:
    """
    Agent phân tích cảm xúc (sentiment) cho văn bản đánh giá.
    Sử dụng model đã train sẵn (joblib) để dự đoán nhãn cảm xúc.
    """

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

    CATEGORICAL_COLS = ['rfm_segment', 'favorite_payment_type', 'customer_state']
    ENCODERS_FILENAME = 'categorical_encoders_experience.pkl'

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        encoders_path: Optional[Union[str, Path]] = None,
        label_map: Optional[Dict[int, str]] = None,
    ):
        if model_path is None:
            model_path = SENTIMENT_MODEL_PATH
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model không tồn tại: {self.model_path}")

        self.pipeline = joblib.load(self.model_path)
        logger.info(f"Loaded model from {self.model_path}")

        if encoders_path is None:
            encoders_path = self.model_path.parent / self.ENCODERS_FILENAME
        encoders_path = Path(encoders_path)

        self.encoders = {}
        if encoders_path.exists():
            with open(encoders_path, 'rb') as f:
                self.encoders = pickle.load(f)
            logger.info(f"Loaded encoders from {encoders_path}")
        else:
            logger.warning(f"Encoders not found at {encoders_path}")

        self.label_map = label_map or {0: "negative", 1: "neutral", 2: "positive"}

    @staticmethod
    def to_python_value(val):
        """Chuyển đổi các kiểu dữ liệu NumPy sang các kiểu dữ liệu Python gốc."""
        if isinstance(val, (np.integer, np.int64, np.int32)):
            return int(val)
        if isinstance(val, (np.floating, np.float64, np.float32)):
            return float(val)
        if isinstance(val, np.ndarray):
            return val.tolist()
        if isinstance(val, (np.bool_, bool)):
            return bool(val)
        if isinstance(val, dict):
            return {k: SentimentAgent.to_python_value(v) for k, v in val.items()}
        if isinstance(val, (list, tuple)):
            return [SentimentAgent.to_python_value(v) for v in val]
        return val

    def _encode_features(self, features: Dict[str, Any]) -> List[float]:
        # Chuyển đổi tất cả các giá trị đầu vào thành dạng cú pháp Python gốc.
        features = self.to_python_value(features)

        full = {name: 0 for name in self.FEATURE_NAMES}
        for col in self.CATEGORICAL_COLS:
            full[col] = 'unknown'

        full.update(features)

        for col in self.CATEGORICAL_COLS:
            encoder = self.encoders.get(col)
            val = full[col]
            if encoder is not None:
                try:
                    full[col] = int(encoder.transform([val])[0])
                except ValueError:
                    logger.warning(f"Unknown value '{val}' for {col}, using 0")
                    full[col] = 0
            else:
                full[col] = 0

        return [full[name] for name in self.FEATURE_NAMES]

    def analyze(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not features:
            return {"label": "unknown", "confidence": 0.0, "proba": {}, "error": "Empty features"}

        try:
            X = np.array([self._encode_features(features)], dtype=np.float64)
            proba = self.pipeline.predict_proba(X)[0]
            label_idx = int(np.argmax(proba))
            confidence = float(proba[label_idx])

            proba_dict = {
                self.label_map.get(i, str(i)): float(p)
                for i, p in enumerate(proba)
            }

            return {
                "label": self.label_map.get(label_idx, str(label_idx)),
                "confidence": confidence,
                "proba": proba_dict,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            return {
                "label": "error",
                "confidence": 0.0,
                "proba": {},
                "error": str(e),
            }

    @classmethod
    def from_config(cls, config_path: Union[str, Path]):
        import json
        config_path = Path(config_path)
        with open(config_path) as f:
            config = json.load(f)
        return cls(
            model_path=config.get("model_path"),
            encoders_path=config.get("encoders_path"),
            label_map=config.get("label_map"),
        )