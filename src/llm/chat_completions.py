from ollama import Client
from config.settings import settings
# https://github.com/ollama/ollama-python
client = Client(
    host=settings.LLM_AGENT_HOST,
)


async def chat_completion(message, id = ''):
    stream = client.chat(
        model=settings.LLM_AGENT_BASE_MODEL,
        messages=[
          {
            'role': 'user',
            'content': message,
          }
        ], stream=True)
    for chunk in stream:
        yield chunk['message']['content']
