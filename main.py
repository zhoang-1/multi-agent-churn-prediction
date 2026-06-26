import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.pipeline import router as pipeline_router

app = FastAPI(
    title="Multi-agent system sentiment analysis and prediction churn in ecommerce",
    version="1.0",
    description="Phân tích cảm xúc khách hàng và dự đoán tỷ lệ rời bỏ dựa trên dữ liệu orders"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gắn router

app.include_router(pipeline_router)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )