# Project Structure

```
project/
├── config/
│   ├── __init__.py
│   └── settings.py  
├── datasets/
├── notebooks/
├── docs/        
    multi_agent_system/
    ├── core/
    │   ├── __init__.py
    │   └── llm_client.py        # call_llm, client init
    ├── agents/
    │   ├── __init__.py
    │   ├── base.py              # Abstract Base Agent (optional)
    │   ├── data_agent.py        # CustomerDataAgent
    │   ├── sentiment_agent.py   # SentimentAgent
    │   ├── churn_agent.py       # ChurnAgent
    │   ├── report_agent.py      # ReportAgent
    │   └── action_agent.py      # ActionAgent
    ├── states/
    │   ├── __init__.py
    │   └── graph_state.py       # Tất cả TypedDict
    ├── graphs/
    │   ├── __init__.py
    │   ├── sentiment_graph.py   # Build sentiment pipeline
    │   ├── churn_graph.py       # Build churn pipeline
    │   └── report_graph.py      # Build report pipeline (và có thể tích hợp data)
    ├── prompts/
    │   ├── report_system.md
    │   └── action_system.md
    ├── tests/
    │   ├── __init__.py
    │   ├── test_sentiment.py
    │   └── test_graphs.py
    ├── scripts/
    │   └── run_pipeline.py      # Chạy demo
    └── main.py                  (optional)
├── main.py
└── README.md