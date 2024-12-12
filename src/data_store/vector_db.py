import qdrant_client
from config.settings import settings
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
import uuid


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
        vectors_config=models.VectorParams(size=0, distance=models.Distance.COSINE),
      )
      print('Created collection:', self.collection_name)

  def set_embeddings_and_texts(self, embeddings, texts):
    self.embeddings = embeddings
    self.texts = texts
    self._update_vector_size()

  def _update_vector_size(self):
    self.client.update_collection(
      collection_name=self.collection_name,
      vectors_config=models.VectorParams(size=self.embeddings.shape[1], distance=models.Distance.COSINE),
    )

  def _prepare_points(self):
    points = []
    for i, embedding in enumerate(self.embeddings):
      points.append(PointStruct(id=str(uuid.uuid4()), vector=embedding.tolist(), payload={"content": self.texts[i]}))
    return points

  def upsert_embeddings(self):
    points = self._prepare_points()
    self.client.upsert(
      collection_name=self.collection_name,
      wait=True,
      points=points
    )
    
embedding_store = EmbeddingStore('collection_name')

# # Example embeddings and texts
# embeddings = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
# texts = ["First text", "Second text"]

# # Set embeddings and texts
# embedding_store.set_embeddings_and_texts(embeddings, texts)

# # Upsert embeddings into the collection
# embedding_store.upsert_embeddings()