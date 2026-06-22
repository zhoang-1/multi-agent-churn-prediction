# LangGraph Workflow

```
                        START

                           ↓

                    CustomerDataAgent
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
     _agentic_lookup()              CustomerLookupTool
          │                                 │
          ▼                                 ▼
        Gemini                        CustomerService
          │                                 │
          └──────────────┬──────────────────┘
                         ▼
                 HarmonizationTool
                         │
                         ▼
                Customer Context
                         │
          ┌──────────────┴──────────────────┐
          ▼                                 ▼
 ChurnFeatureBuilder            SentimentFeatureBuilder

        │                                   │

        ▼                                   ▼

    Sentiment                             Churn

        │                                   │

        ─────────────────────────────────────

                         ↓

                        Report

                         ↓

                        Action

                         ↓

                        END
```

## State

State gồm

- Customer Profile

- Sentiment Result

- Churn Result

- Report

- Action