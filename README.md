# rag

```bash
uvicorn main:app --reload
celery -A worker.celery_worker.celery_app worker --loglevel=info 
```