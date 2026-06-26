# graphs/sentiment_graph.py
from langgraph.graph import StateGraph, END
from ..state.graph_state import SentimentState
from ..agents.sentiment_agent import SentimentAgent
from churn_prediction.paths import SENTIMENT_MODEL_PATH
from ..builders.sentiment_feature_builder import SentimentFeatureBuilder

# ── Khởi tạo agent ────────────────────────────────────────────────────────────
sentiment_agent = SentimentAgent(str(SENTIMENT_MODEL_PATH))
sentiment_feature_builder = SentimentFeatureBuilder()

def node_sentiment(state: SentimentState) -> SentimentState:
    print("=" * 50)
    print("STATE IN SENTIMENT")
    print(state.keys())
    print(state.get("customer_profile"))
    print("=" * 50)
    try:
        features = state.get("features")
        
        # Nếu chưa có features truyền vào, tự động build từ profile
        if not features:
            profile = state.get("customer_profile")
            if profile:
                features = sentiment_feature_builder.build(profile)
                print(len(features))   # In ra 30
                print(sorted(features.keys()) == sorted(SentimentFeatureBuilder.FEATURE_NAMES))  # True
        
        if not features:
            raise ValueError("Không có features hoặc customer_profile để build")
            
        result = sentiment_agent.analyze(features)
        return {**state, "features": features, "sentiment_result": result}
    except Exception as e:
        return {**state, "error": f"SentimentAgent: {e}"}

def build_sentiment_pipeline():
    graph = StateGraph(SentimentState)
    graph.add_node("sentiment", node_sentiment)
    graph.set_entry_point("sentiment")
    graph.add_edge("sentiment", END)
    return graph.compile()  

# ── Compile sẵn để import ──────────────────────────────────────────────────────
sentiment_pipeline = build_sentiment_pipeline()