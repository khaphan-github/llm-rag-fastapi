from celery import Celery
from config.settings import settings
from uploader.file_reader import LocalFileReader, FileConverter
from pre_processing.vector_embedding import Preprocessor
from llm.sentence_transformers import singleton_model
from data_store.vector_db import embedding_store

## Class publish event to celery queue with message file path, file id, with key embedding_job
## Connectoion be delclared in .env file CELERY_BROKER_URL
# Load the CELERY_BROKER_URL from the environment variables
##  celery -A worker.celery_worker.celery_app worker --loglevel=info 
# Initialize the Celery app
celery_app = Celery('publisher', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_BROKER_URL)

celery_app.conf.update(
  broker_connection_retry_on_startup=True,
  worker_concurrency=4
)
class CeleryPublisher:
  def __init__(self):
    self.app = celery_app

  def publish_event(self, file_path, file_id, key='embedding_job'):
    message = {
      'file_path': file_path,
      'file_id': file_id,
      'key': key
    }
    self.app.send_task('tasks.process_file', args=[message])
    print(f"Publishing event to Celery with message: {message}")

@celery_app.task(name='tasks.process_file', rate_limit='20/m', max_retries=2)
def process_file(message):
  try:
    file_path = message['file_path']
    file_id = message['file_id']
    key = message['key']

    ## Read file then handle preprocessing function
    file_converter = FileConverter()
    local_file_reader = LocalFileReader(file_converter)
    
    file_type = "md"
    content = local_file_reader.read(file_path, file_type)
    
    preprocessor = Preprocessor(content)
    text_chunks = preprocessor.text_chunks
    ## Embedding
    embeddings = singleton_model.encode(text_chunks)
    
    # Upsert embeddings into the collection
    embedding_store.set_embeddings_and_texts(embeddings, text_chunks)
    embedding_store.upsert_embeddings()
    ## Save to vectordb
    ## Remove job from queue
    ## Call API notify
    # Remove job from queue
    local_file_reader.remove(file_path)
    
    celery_app.backend.mark_as_done(message['file_id'], result='done')
    
    # Call API to notify
    print(f"Successfully notified API for file_id: {file_id}")
  except Exception as exc:
    if process_file.request.retries >= 2:
      print(f"Failed to process file {file_id} after 2 retries: {exc}")
    else:
      print(f"Error processing file {file_id}: {exc}")
      raise process_file.retry(exc=exc)