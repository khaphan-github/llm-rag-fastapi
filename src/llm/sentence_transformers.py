import torch
from sentence_transformers import SentenceTransformer
from config.settings import settings


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SentenceTransformerSingleton(metaclass=SingletonMeta):
    def __init__(self, model_name=settings.LLM_BASE_MODEL, cache_folder='./llm_cache'):
        print('Creating SentenceTransformerSingleton instance...')
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(
            model_name, cache_folder=cache_folder, device=device)
        print(
            f'Creating SentenceTransformerSingleton instance... Done! cuda: {torch.cuda.is_available()}')

    def encode(self, texts):
        return self.model.encode(texts)


# Initialize the singleton instance when the module is imported
singleton_model = SentenceTransformerSingleton()

# Usage
# embeddings = singleton_model.encode(texts)
