from fastapi import FastAPI
from app.api.knowledge import router as knowledge_router

app = FastAPI(
    title="Enterprise Knowledge Platform",
    version="1.0.0"
)

app.include_router(knowledge_router)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "platform": "Enterprise Knowledge Platform"
    }
