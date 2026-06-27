from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.churn_prediction.multi_agents.services.pipeline_service import PipelineService
from src.churn_prediction.multi_agents.services.customer_service import CustomerService
customer_service = CustomerService()
router = APIRouter(
        prefix="/api",
        tags=["Multi-Agent Pipeline"]
    )
router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)
class CustomerRequest(BaseModel):
    customer_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

@router.get("/")
def health_check():
    return {
    "status": "running",
    "service": "multi-agent-churn-prediction"
    }
@router.get("")
def get_all_customers(
    page: int = 1,
    limit: int = 20
):
    return {
        "success": True,
        **customer_service.get_all_customers(page, limit)
    }
@router.post("/data")
def run_data_pipeline(request: CustomerRequest):
    try:
        result = PipelineService.run_data_pipeline(
            request.model_dump()
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/sentiment")
def run_sentiment_pipeline(request: CustomerRequest):
    try:
        result = PipelineService.run_sentiment_pipeline(
            request.model_dump()
        )

        return {
            "success": True,
            "sentiment": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/churn")
def run_churn_pipeline(request: CustomerRequest):

    try:
        result = PipelineService.run_churn_pipeline(
             request.model_dump()
        )

        return {
            "success": True,
            "churn": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/report")
def run_report_pipeline(request: CustomerRequest):

    try:
        result = PipelineService.run_report_pipeline(
            request.model_dump()
        )

        return {
            "success": True,
            "report": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/pipeline")
def run_full_pipeline(request: CustomerRequest):

    try:
        result = PipelineService.run(
            request.customer_id
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

