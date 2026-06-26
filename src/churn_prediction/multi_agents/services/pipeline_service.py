from ..graph.data_graph import data_pipeline
from ..graph.sentiment_graph import sentiment_pipeline
from ..graph.churn_graph import churn_pipeline
from ..graph.report_graph import report_pipeline
import traceback
from ..builders.sentiment_feature_builder import SentimentFeatureBuilder
from ..builders.churn_feature_builder import ChurnFeatureBuilder
from ..agents.sentiment_agent import SentimentAgent
from ..agents.churn_agent import ChurnAgent

class PipelineService:


    @staticmethod
    def run(order_input: str):

        try:

            # ==========================
            # STEP 1 - DATA PIPELINE
            # ==========================
            data_state = data_pipeline.invoke({
                "order_input": order_input,
                "customer_profile": None,
                "sentiment_ready": None,
                "sentiment_result": None,
                "sentiment_summary": None,
                "features": None,
                "churn_result": None,
                "churn_summary": None,
                "report": None,
                "action_plan": None,
                "error": None,
            })

            data_result = data_pipeline.invoke(data_state)

            # ==========================
            # STEP 2 - SENTIMENT PIPELINE
            # ==========================
            sentiment_result = sentiment_pipeline.invoke(
                data_result
            )

            # ==========================
            # STEP 3 - CHURN PIPELINE
            # ==========================
            churn_result = churn_pipeline.invoke(
                sentiment_result
            )

            # ==========================
            # STEP 4 - REPORT PIPELINE
            # ==========================
            report_result = report_pipeline.invoke(
                churn_result
            )
            # ==========================
            # STEP 5 - ACTION PIPELINE
            # ==========================

            return {
                "success": True,
                "data": data_result,
                "sentiment": sentiment_result,
                "churn": churn_result,
                "report": report_result
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }


    @staticmethod
    def run_data_pipeline(order_input: dict)-> dict:
        return data_pipeline.invoke({
            "order_input": order_input,
            "customer_profile": None,
            "sentiment_ready": None,
            "sentiment_result": None,
            "sentiment_summary": None,
            "features": None,
            "churn_result": None,
            "churn_summary": None,
            "report": None,
            "action_plan": None,
            "error": None,
        })


    @staticmethod
    def run_sentiment_pipeline(order_input: dict):
        
        data_result = PipelineService.run_data_pipeline(order_input)
        try:
            print("========== BEFORE SENTIMENT ==========")
            profile = data_result["customer_profile"]
            builder = SentimentFeatureBuilder()
            features = builder.build(profile)
            features = SentimentAgent.to_python_value(features)
            data_result["features"] = features
            result = sentiment_pipeline.invoke(data_result)
            return result

        except Exception as e:
            print("========== SENTIMENT ERROR ==========")
            traceback.print_exc()
            raise


    @staticmethod
    def run_churn_pipeline(order_input: dict):
        data_result = PipelineService.run_data_pipeline(order_input)
        try:
            profile = data_result.get("customer_profile")
            builder = ChurnFeatureBuilder()
            features = builder.build(profile)
            data_result["features"] = features
            result = churn_pipeline.invoke(data_result)
            
            return result
        except Exception as e:
            print("========== SENTIMENT ERROR ==========")
            traceback.print_exc()
            # Trả về dict lỗi nếu cần
            return {"error": str(e)}

    @staticmethod
    def run_report_pipeline(order_input: dict):
        try:
            # Chạy sentiment pipeline
            sentiment_state = PipelineService.run_sentiment_pipeline(order_input)

            if sentiment_state.get("error"):
                return sentiment_state

            # Chạy churn pipeline
            churn_state = PipelineService.run_churn_pipeline(order_input)

            if churn_state.get("error"):
                return churn_state
            
            # Tạo state chỉ gồm dữ liệu Report Agent cần
            report_state = {
                "sentiment_result": sentiment_state.get("sentiment_result"),
                "churn_result": churn_state.get("churn_result"),
                "report": None,
                "action_plan": None,
                "error": None,
            }
            
            # Invoke Report Graph
            result = report_pipeline.invoke(report_state)

            return result

        except Exception as e:
            print("========== REPORT ERROR ==========")
            traceback.print_exc()
            return {"error": str(e)}

