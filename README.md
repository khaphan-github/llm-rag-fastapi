# Retrieval Augmented Generation FastAPI - Celery
![Project Logo](./docs/image.png)

## This project will resolve:
1. Provide a full solution to build a RAG system in an enterprise with your own data without pre-training and fine-tuning (Costly).
2. Host yourself: You can set up on your on-premises server or other cloud providers.
3. Use GPU to improve performance.
4. Many deployment solutions: k8s, AWS, Docker, horizontal scaling.

## Tech stack
- RAG architecture.
- FastAPI: Main thread handles requests.
- Celery Worker handles embedding documents then stores them to VectorDB.
- Qdrant as a VectorDB to store embeddings.
- Vietnamese LLM sentence-transformer.
- Docker, K8S.

## Compare pricincing self host and use cloud (openai api):
// Table to compare:


## Concept:
### What is RAG?
### Sentence transformer:
### Vector embedding:
### Retrival:
### Time and latentcy:

 
## Workflow:

## Run in your local 

```bash
pip3 install -r requirements.txt
uvicorn main:app --reload
celery -A worker.celery_worker.celery_app worker --loglevel=info 
```
## Setup cluster:
### Docker:
### K8S:
### AWS: