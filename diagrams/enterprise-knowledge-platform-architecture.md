# Enterprise Knowledge Platform Architecture

```mermaid
graph TD
    ACP[Agentic Control Plane]

    ACP --> EKP[Enterprise Knowledge Platform]

    EKP --> D[Document Agent]
    EKP --> S[Search Agent]
    EKP --> KG[Knowledge Graph Agent]
    EKP --> R[Recommendation Agent]

    D --> W[Knowledge Workflow]
    S --> W
    KG --> W
    R --> W

    W --> KR[Enterprise Knowledge Repository]
