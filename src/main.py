from fastapi import FastAPI
from fastapi import UploadFile, File
import os
import asyncio
from fastapi import FastAPI, UploadFile, File
from uploader.uploader import LocalFileUploader
from worker.celery_worker import CeleryPublisher
from config.settings import settings

app = FastAPI()
publisher = CeleryPublisher()

upload_dir = settings.UPLOAD_DIR
local_uploader = LocalFileUploader(upload_dir=upload_dir)

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    # UPLOADER
    file_path = os.path.join(upload_dir, file.filename)
    file_content = await file.read()
    local_uploader.upload(file_path, file_content)

    # Publisher    
    await asyncio.to_thread(publisher.publish_event, file_path, file.filename)
    
    return {"filename": file.filename, "file_path": file_path}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}