from app.services.text_processing import chunk_text, extract_text


class DocumentAgent:
    """Validates supported text documents and prepares searchable chunks."""

    def process(self, filename: str, content: bytes):
        text = extract_text(filename, content)
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("Document did not produce any searchable chunks.")
        return {"text": text, "chunks": chunks, "status": "processed"}
