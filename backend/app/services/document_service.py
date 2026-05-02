import io
import os
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


class DocumentService:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=120,
        )

    def extract_text(self, filename: str, file_bytes: bytes) -> str:
        extension = os.path.splitext(filename or "")[1].lower()

        if extension == ".pdf":
            return self._extract_pdf(file_bytes)
        if extension == ".docx":
            return self._extract_docx(file_bytes)
        if extension in {".txt", ".md"}:
            return file_bytes.decode("utf-8", errors="ignore")

        raise ValueError(f"Unsupported document type: {extension or 'unknown'}")

    def chunk_text(self, text: str) -> List[str]:
        cleaned = " ".join(text.split())
        if not cleaned:
            return []
        return self.splitter.split_text(cleaned)

    def find_relevant_chunks(self, query: str, text: str, limit: int = 3) -> List[dict]:
        chunks = self.chunk_text(text)
        if not chunks:
            return []

        lowered_query = (query or "").strip().lower()
        query_terms = [term for term in lowered_query.split() if term]

        scored = []
        for idx, chunk in enumerate(chunks):
            lowered_chunk = chunk.lower()
            score = 0
            if not query_terms:
                score = max(1, len(chunk))
            else:
                score = sum(lowered_chunk.count(term) for term in query_terms)
            if score > 0:
                scored.append((score, idx, chunk))

        if not scored:
            scored = [(1, idx, chunk) for idx, chunk in enumerate(chunks[:limit])]

        scored.sort(key=lambda item: (-item[0], item[1]))

        return [
            {
                "product_id": f"document_chunk_{idx}",
                "name": chunk.split('\n')[0][:50] if '\n' in chunk else f"Catalog: {chunk[:30]}...",
                "description": chunk,
                "result_type": "document",
                "graph_context": {
                    "category": "Document Resource",
                    "brand": "From Uploaded File",
                    "reviews": ["Extracted from your PDF catalog."]
                },
            }
            for position, (_, idx, chunk) in enumerate(scored[:limit])
        ]

    def _extract_pdf(self, file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _extract_docx(self, file_bytes: bytes) -> str:
        from docx import Document

        document = Document(io.BytesIO(file_bytes))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)


document_service = DocumentService()
