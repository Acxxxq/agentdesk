# Architecture

**Languages:** English | [简体中文](zh/ARCHITECTURE.md)

The first module is a read-only message interpreter. It returns a structured understanding that a later policy layer can review before changing task state.

```mermaid
flowchart LR
    UI[Chat demo or client] --> API[FastAPI]
    API --> REQ[Validated request and read-only context]
    REQ --> LLM[Anthropic SDK provider]
    LLM --> CONTRACT[Strict Pydantic contract]
    CONTRACT --> EVIDENCE[Task reference and source evidence checks]
    EVIDENCE --> RESULT[Acts, relations, and ambiguities]
    DATA[Fixed evaluation dataset] --> EVAL[HTTP evaluator]
    API --> EVAL
    EVAL --> RECORD[Versioned results and source snapshots]
```

The interpreter does not own conversations, create tasks, answer customers, or execute tools. The API validates request bounds; the model proposes semantic acts; server-side validation rejects malformed structures, unsupported task references, and entities without literal evidence in the current message.

`MessageUnderstanding` is an interpretation result, not an authorization decision. The next planned module will add a deterministic dialogue policy, explicit clarification decisions, and a pure state reducer. Persistence and external tools follow that boundary.

Everything currently needed for the first module runs in Docker: one API container, plus an optional test profile. The model key remains local in `.env`. Evaluation datasets and immutable run records live in the repository-level [`evaluation/`](../evaluation/README.md) folder.
