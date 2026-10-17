# The workflow

```mermaid
flowchart TD
    A[You + your coding agent] -->|Agree on categories and examples| R[Your saved rubric]
    G[Gmail connector] -->|Complete conversations| C[Your coding agent]
    C --> P[pipeline.py]
    R --> P
    K[Your private Jev key] --> P
    P --> J[Jev applies the rubric]
    J --> N[Needs action]
    J --> W[Worth seeing]
    J --> S[Skip]
    N --> V[Review together in chat]
    W --> V
    S --> V
    V -->|Approve a reusable example| R
```

The in-chat review interface is optional. The same results can be shown as a numbered list or a local review page. A correction is saved for that email; a separately approved teaching example helps with future judgments.
