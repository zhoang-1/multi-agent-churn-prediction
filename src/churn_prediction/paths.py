# olist_churn_prediction/paths.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# DATA DIRECTORIES
DATA_DIR     = PROJECT_ROOT / "data"
# data olist
OLIST_DIR    = DATA_DIR / "olist"
RAW_DIR      = OLIST_DIR / "raw"
PROCESSED_DIR = OLIST_DIR / "processed"   # Dữ liệu đã clean, sẵn sàng cho feature engineering
FEATURES_DIR = OLIST_DIR / "features"     # Dữ liệu sau feature engineering
EXTERNAL_DIR = OLIST_DIR / "external"     # Dữ liệu từ bên ngoài (nếu có)
INTERIM_NOTEBOOK_DIR = OLIST_DIR / "interim/notebook_related" # Dữ liệu tạm thời trong quá trình phân tích, có thể xóa sau khi hoàn thành notebook
INTERIM_CLI_DIR = OLIST_DIR / "interim/cli_related"     # Dữ liệu tạm thời trong quá trình phát triển CLI, có thể xóa sau khi hoàn thành CLI
# data online_retail
ONLINE_RETAIL_DIR = DATA_DIR / "online_retail"
ONLINE_RETAIL_RAW_DIR = ONLINE_RETAIL_DIR / "raw"
PROCESSED_ONLINE_RETAIL_DIR = ONLINE_RETAIL_DIR / "processed"
FEATURES_ONLINE_RETAIL_DIR = ONLINE_RETAIL_DIR / "features"
EXTERNAL_ONLINE_RETAIL_DIR = ONLINE_RETAIL_DIR / "external"
INTERIM_NOTEBOOK_ONLINE_RETAIL_DIR = ONLINE_RETAIL_DIR / "interim/notebook_related"
INTERIM_CLI_ONLINE_RETAIL_DIR = ONLINE_RETAIL_DIR / "interim/cli_related"
# MODELING DIRECTORIES
MODELS_DIR = PROJECT_ROOT / "models"            # Lưu model đã train
MODELS_OLIST_DIR = MODELS_DIR / "Olist"              # Lưu model cuối cùng đã chọn
MODELS_ONLINE_RETAIL_DIR = MODELS_DIR / "Online_Retail"  # Lưu model cuối cùng đã chọn
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"    # Lưu checkpoint trong quá trình train
# thư mục mã nguồn 
SRC_DIR = PROJECT_ROOT / "src"
FEATURES_SRC_DIR = SRC_DIR / "features"  # Code tạo features
MODELS_SRC_DIR  = SRC_DIR  / 'models'    # Code định nghĩa model
VISUALIZATION_SRC_DIR = SRC_DIR / "visualization"  # Code vẽ biểu đồ
# reports
REPORTS_DIR = PROJECT_ROOT / 'reports'
FIGURES_DIR = REPORTS_DIR / "figures"           # Lưu hình ảnh, biểu đồ
LOGS_DIR = REPORTS_DIR / "logs"                 # Lưu log files
METRICS_DIR = REPORTS_DIR / "metrics"           # Lưu kết quả đánh giá model
# CONFIG & ENVIRONMENT
CONFIG_DIR = PROJECT_ROOT / "configs"            # File cấu hình (yaml, json)
ENV_DIR = PROJECT_ROOT / "env"                  # Môi trường ảo, requirements.txt
# NOTEBOOKS
NOTEBOOKS_DIR = PROJECT_ROOT / "notebook"       # Tất cả notebook
# TESTS
TESTS_DIR = PROJECT_ROOT / "tests"            # Code test, có thể chia thành unit tests và integration tests
# TẠO TẤT CẢ THƯ MỤC NẾU CHƯA TỒN TẠI

directories_to_create = [
    RAW_DIR, OLIST_DIR, INTERIM_NOTEBOOK_DIR, INTERIM_CLI_DIR, PROCESSED_DIR, FEATURES_DIR, EXTERNAL_DIR,
    ONLINE_RETAIL_RAW_DIR, PROCESSED_ONLINE_RETAIL_DIR, FEATURES_ONLINE_RETAIL_DIR, EXTERNAL_ONLINE_RETAIL_DIR, INTERIM_NOTEBOOK_ONLINE_RETAIL_DIR, INTERIM_CLI_ONLINE_RETAIL_DIR,
    MODELS_DIR, MODELS_OLIST_DIR, MODELS_ONLINE_RETAIL_DIR, CHECKPOINTS_DIR,
    FEATURES_SRC_DIR, MODELS_SRC_DIR, VISUALIZATION_SRC_DIR,
    REPORTS_DIR, FIGURES_DIR, LOGS_DIR, METRICS_DIR,
    NOTEBOOKS_DIR, INTERIM_NOTEBOOK_DIR,
    CONFIG_DIR, ENV_DIR,
    TESTS_DIR
]

for dir_path in directories_to_create:
    dir_path.mkdir(parents=True, exist_ok=True)

print("All directories created successfully!")

# TIỆN ÍCH CHO VIỆC LƯU/ĐỌC DỮ LIỆU
def get_latest_file(directory: Path, pattern: str = "*.parquet"):
    """Lấy file mới nhất trong thư mục"""
    files = list(directory.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)

def ensure_dir(path: Path):
    """Đảm bảo thư mục tồn tại"""
    path.mkdir(parents=True, exist_ok=True)
    return path