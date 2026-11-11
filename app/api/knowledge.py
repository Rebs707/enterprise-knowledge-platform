from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.agents.document_agent import DocumentAgent
from app.agents.search_agent import SearchAgent
from app.services.knowledge_store import KnowledgeStore
from app.services.text_processing import InvalidDocumentError, UnsupportedDocumentError

router = APIRouter()
store = KnowledgeStore()
document_agent = DocumentAgent()
search_agent = SearchAgent(store=store)
MAX_UPLOAD_BYTES = 2 * 1024 * 1024


@router.post("/documents", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    raw_content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Maximum upload size is 2 MiB.")

    safe_filename = file.filename.replace("\\", "/").split("/")[-1]
    try:
        processed = document_agent.process(safe_filename, raw_content)
    except UnsupportedDocumentError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    suffix = Path(safe_filename).suffix.lower()
    content_type = "text/markdown" if suffix == ".md" else "text/plain"
    result = store.add_document(
        filename=safe_filename,
        content_type=content_type,
        raw_content=raw_content,
        chunks=processed["chunks"],
    )
    return {"status": "indexed", **result}


@router.get("/documents/{document_id}")
def get_document(document_id: str):
    document = store.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.get("/search")
def search_documents(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(10, ge=1, le=50),
):
    result = search_agent.search(q, limit=limit)
    return result


@router.get("/knowledge/{topic}")
def knowledge(topic: str):
    """Compatibility route; now performs real keyword retrieval."""
    return search_agent.search(topic)
