from underthesea import sent_tokenize, text_normalize
from sklearn.metrics.pairwise import cosine_similarity
import re
from transformers import AutoModel, AutoTokenizer
import torch
import numpy as np
from config.settings import settings

class Preprocessor:
  def __init__(self, text):
    self.text = text
    self.text_chunks = self.tokenize_and_normalize()

  def tokenize_and_normalize(self):
    if self.text:
      chunks = self.chunk_text(self.text)
      return [chunk for chunk in chunks if len(chunk) >= 128]
    else:
      return []
    
  def chunk_text_by_sentences(self, text):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return sentences
  
  def _combine_sentences(self, sentences):
    combined_sentences = []
    for i in range(len(sentences)):
        combined_sentence = sentences[i]
        if i > 0:
            combined_sentence = sentences[i-1] + ' ' + combined_sentence
        if i < len(sentences) - 1:
            combined_sentence += ' ' + sentences[i+1]
        combined_sentences.append(combined_sentence)
    return combined_sentences
  
  
  def _calculate_cosine_distances(self, embeddings):
      distances = []
      for i in range(len(embeddings) - 1):
          similarity = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
          distance = 1 - similarity
          distances.append(distance)
      return distances


  def get_embeddings(self, texts, model_name=settings.LLM_BASE_MODEL):
      tokenizer = AutoTokenizer.from_pretrained(model_name)
      model = AutoModel.from_pretrained(model_name)

      encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

      with torch.no_grad():
          model_output = model(**encoded_input)
      
      embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

      return embeddings.numpy()


  def mean_pooling(self, model_output, attention_mask):
      token_embeddings = model_output[0]  
      input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
      return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


  def chunk_text(self, text, breakpoint_percentile_threshold=80):
      single_sentences_list = self.chunk_text_by_sentences(text)
      combined_sentences = self._combine_sentences(single_sentences_list)
      embeddings = self.get_embeddings(combined_sentences)
      distances = self._calculate_cosine_distances(embeddings)

      # Determine the threshold distance for identifying breakpoints based on the 80th percentile of all distances.
      breakpoint_distance_threshold = np.percentile(distances, breakpoint_percentile_threshold)

      # Find all indices where the distance exceeds the calculated threshold, indicating a potential chunk breakpoint.
      indices_above_thresh = [i for i, distance in enumerate(distances) if distance > breakpoint_distance_threshold]
    
      chunks = []
      start_index = 0
      
      for index in indices_above_thresh:
          chunk = ' '.join(single_sentences_list[start_index:index+1])
          chunks.append(chunk)
          start_index = index + 1

      # If there are any sentences left after the last breakpoint, add them as the final chunk.
      if start_index < len(single_sentences_list):
          chunk = ' '.join(single_sentences_list[start_index:])
          chunks.append(chunk)

      return [chunk for chunk in chunks if chunk]
