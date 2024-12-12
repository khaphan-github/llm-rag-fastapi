import os
import asyncio
from fastapi import FastAPI, UploadFile, File
from uploader.uploader import LocalFileUploader
from worker.celery_worker import CeleryPublisher
from config.settings import settings
from config.system_prompt import SYSTEM_PROMPT
from data_store.vector_db import embedding_store
from llm.sentence_transformers import singleton_model
from pydantic import BaseModel
import uuid

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
@app.post("/search/")
def search_similar(search_query: SearchQuery):
    # Assuming you have a model to encode the query into an embedding
    embeddings = singleton_model.encode([search_query.query])
    search_result = embedding_store.search_similar(embeddings[0], 3)
    system_data = [e.payload['content'] for e in search_result]
    return {"answer": f"{SYSTEM_PROMPT} User query: {search_query.query} System Data: {system_data}" }