import qdrant_client
from config.settings import settings
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
import uuid
import time
## https://f33bfb76-8b21-4510-b0bc-709059915726.us-east4-0.gcp.cloud.qdrant.io:6333/dashboard#/collections/collection_name#points

class EmbeddingStore:
  _instance = None

  def __new__(cls, collection_name):
    if cls._instance is None:
      cls._instance = super(EmbeddingStore, cls).__new__(cls)
      cls._instance.collection_name = collection_name
      cls._instance.client = qdrant_client.QdrantClient(url=settings.QDRANT_CLIENT_URL, api_key=settings.QDRANT_CLIENT_API_KEY)
      cls._instance._create_collection()
    return cls._instance

  def _create_collection(self):
    try:
      self.client.get_collection(self.collection_name)
    except Exception as e:
      self.client.recreate_collection(
        collection_name=self.collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
      )
      print('Created collection:', self.collection_name)

  def set_embeddings_and_texts(self, embeddings, texts):
    self.embeddings = embeddings
    self.texts = texts

  def _prepare_points(self):
    points = []
    for i, embedding in enumerate(self.embeddings):
      points.append(PointStruct(id=str(uuid.uuid4()), vector=embedding.tolist(), payload={"content": self.texts[i]}))
    return points

  def upsert_embeddings(self, chunk_size=32):
    points = self._prepare_points()
    for i in range(0, len(points), chunk_size):
      chunk = points[i:i + chunk_size]
      self.client.upsert(
        collection_name=self.collection_name,
        wait=True,
        points=chunk
      )
      time.sleep(0.1)  # Delay 100ms before the next call

  def search_similar(self, query_embedding, limit=8):
    search_result = self.client.search(
      collection_name=self.collection_name,
      query_vector=query_embedding.tolist(),
      limit=limit
    )
    return search_result

embedding_store = EmbeddingStore('collection_name')

# Example usage:
# embeddings = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
# texts = ["First text", "Second text"]

# Set embeddings and texts
# embedding_store.set_embeddings_and_texts(embeddings, texts)

# Upsert embeddings into the collection
# embedding_store.upsert_embeddings()

# Search for similar embeddings
# query_embedding = model.encode(['Thông tin cơ bản về HUTECH:'])[0]
# search_result = embedding_store.search_similar(query_embedding)
# print(search_result)