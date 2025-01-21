import os
import asyncio
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from uploader.uploader import LocalFileUploader
from celery_worker import CeleryPublisher
from config.settings import settings
from config.system_prompt import SYSTEM_PROMPT
from data_store.vector_db import embedding_store
from llm.sentence_transformers import singleton_model
from llm.chat_completions import chat_completion
from pydantic import BaseModel
import uuid
import logging

app = FastAPI()

publisher = CeleryPublisher()

upload_dir = settings.UPLOAD_DIR
local_uploader = LocalFileUploader(upload_dir=upload_dir)


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        
        new_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        new_file_path = os.path.join(upload_dir, new_filename)
        
        await asyncio.to_thread(local_uploader.upload, new_file_path, file_content)
        await asyncio.to_thread(publisher.publish_event, new_file_path, file.filename)
        
        return {"status": "success", "original_filename": file.filename, "new_filename": new_filename, "new_file_path": new_file_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class SearchQuery(BaseModel):
    query: str

# IT wll return stream.
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/completion/")
async def search_similar(search_query: SearchQuery):
    logger.info("Received search query: %s", search_query.query)
    
    # Assuming you have a model to encode the query into an embedding
    embeddings = singleton_model.encode([search_query.query])
    logger.info("Encoded query into embeddings: %s", embeddings)
    
    search_result = embedding_store.search_similar(embeddings[0], 3)
    logger.info("Search results: %s", search_result)
    
    system_data = [e.payload['content'] for e in search_result]
    logger.info("System data extracted from search results: %s", system_data)
    
    prompt = f"{SYSTEM_PROMPT} User query: {search_query.query}. Get most suitable data to interact with user query follow this System Data: {system_data}"
    logger.info("Constructed prompt for chat completion: %s", prompt)
    
    async def stream_response():
        async for chunk in chat_completion(prompt):
            yield chunk
    return StreamingResponse(stream_response(), media_type="text/plain")

@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
