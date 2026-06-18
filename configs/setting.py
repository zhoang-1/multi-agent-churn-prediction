# config/settings.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# Đường dẫn model (tùy chỉnh theo cây thư mục của bạn)
SENTIMENT_MODEL_PATH = BASE_DIR / "churn_prediction" / "sentiment_model.joblib"
CHURN_MODEL_PATH = BASE_DIR / "churn_prediction" / "churn_model.joblib"