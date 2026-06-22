from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Fact API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChurnRequest(BaseModel):
    age: int
    tenure: int
    monthly_charges: float
    contract_type: str

@app.post("/predict")
def predict_churn(request: ChurnRequest):
    # Mock prediction logic
    prob = 0.5 + (request.monthly_charges / 200.0) - (request.tenure / 100.0)
    prob = max(0.0, min(1.0, prob))
    return {
        "churn_probability": round(prob, 4),
        "prediction": "Churn" if prob > 0.5 else "Stay"
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to Fact API"}

@app.get("/status")
def status():
    return {"status": "ok"}
