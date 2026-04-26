import os
import base64
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal Graph RAG E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    image_b64: Optional[str] = None
    product_id: Optional[str] = None
    document_context: Optional[str] = None

class SearchRequest(BaseModel):
    query: Optional[str] = None
    image_b64: Optional[str] = None

def get_ai_service():
    try:
        from app.services.ai_service import ai_service
        return ai_service
    except Exception as e:
        logger.exception("Failed to load AI service: %s", e)
        return None

def get_vector_service():
    try:
        from app.services.vector_service import vector_service
        return vector_service
    except Exception as e:
        logger.exception("Failed to load vector service: %s", e)
        return None

def get_graph_service():
    try:
        from app.services.graph_service import graph_service
        return graph_service
    except Exception as e:
        logger.exception("Failed to load graph service: %s", e)
        return None

def get_document_service():
    try:
        from app.services.document_service import document_service
        return document_service
    except Exception as e:
        logger.exception("Failed to load document service: %s", e)
        return None

@app.get("/")
def read_root():
    return {"message": "Multimodal Graph RAG E-Commerce API is running"}

@app.get("/health")
def health():
    # Keep container healthchecks lightweight so service startup retries
    # do not make Docker mark the API as unhealthy.
    return {"status": "ok"}

@app.post("/search")
async def search(request: SearchRequest):
    try:
        vector_service = get_vector_service()
        graph_service = get_graph_service()

        if vector_service is None:
            raise HTTPException(status_code=503, detail="Vector service is unavailable")

        results = vector_service.search_multimodal(
            text=request.query, 
            image_b64=request.image_b64
        )
        if not results and graph_service and request.query and not request.image_b64:
            results = graph_service.search_products(request.query)
        # Enrich results with graph context
        enriched = []
        for res in results:
            context = graph_service.get_related_context(res["product_id"]) if graph_service else None
            enriched.append({**res, "graph_context": context})
        return enriched
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-multimodal")
async def search_multimodal(
    query: Optional[str] = Form(None),
    image: UploadFile | None = File(None),
    document: UploadFile | None = File(None),
):
    try:
        vector_service = get_vector_service()
        graph_service = get_graph_service()
        document_service = get_document_service()

        results = []
        image_b64 = None

        if image is not None:
            image_bytes = await image.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        if vector_service is not None and (query or image_b64):
            results = vector_service.search_multimodal(
                text=query,
                image_b64=image_b64,
            )

        if not results and graph_service and query and not image_b64:
            results = graph_service.search_products(query)

        enriched = []
        for res in results:
            context = graph_service.get_related_context(res["product_id"]) if graph_service else None
            enriched.append({**res, "result_type": "product", "graph_context": context})

        if document is not None and document_service is not None:
            document_bytes = await document.read()
            document_text = document_service.extract_text(document.filename or "document", document_bytes)
            document_results = document_service.find_relevant_chunks(query or "", document_text)
            enriched.extend(document_results)

        return enriched
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        ai_service = get_ai_service()
        graph_service = get_graph_service()

        if ai_service is None:
            raise HTTPException(status_code=503, detail="AI service is unavailable")

        context_str = ""
        if request.product_id and graph_service:
            context = graph_service.get_related_context(request.product_id)
            if context:
                context_str = f"\nProduct Context from Graph: Brand: {context['brand']}, Category: {context['category']}, Reviews: {', '.join(context['reviews'])}"
        if request.document_context:
            context_str += f"\nDocument Context: {request.document_context}"

        full_prompt = f"User Message: {request.message}\n{context_str}\nYou are a Product Intelligence Assistant. Answer the user based on the context provided."
        
        # Save temp image if provided for Gemini
        temp_img_path = None
        if request.image_b64:
            temp_img_path = "temp_chat_img.png"
            with open(temp_img_path, "wb") as f:
                f.write(base64.b64decode(request.image_b64))

        response = await ai_service.generate_response(full_prompt, temp_img_path)
        
        if temp_img_path and os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_product(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    brand: str = Form(...),
    product_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        vector_service = get_vector_service()
        graph_service = get_graph_service()

        # Read and encode image
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode('utf-8')
        
        # 1. Add to Vector DB (Weaviate)
        if vector_service:
            vector_service.add_product(name, description, image_b64, product_id)
        
        # 2. Add to Graph DB (Neo4j)
        if graph_service:
            graph_service.add_product_node(product_id, name, description, category, brand)
        
        return {"status": "success", "product_id": product_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
