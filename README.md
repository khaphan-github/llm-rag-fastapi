# rag

```bash
pip3 install -r requirements.txt
uvicorn main:app --reload
celery -A worker.celery_worker.celery_app worker --loglevel=info 
```