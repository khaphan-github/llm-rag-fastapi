from underthesea import sent_tokenize, text_normalize

class Preprocessor:
  def __init__(self, text):
    self.text = text
    self.text_chunks = self.tokenize_and_normalize()

  def tokenize_and_normalize(self):
    if self.text:
      return sent_tokenize(text_normalize(self.text))
    else:
      return []

# Usage
# preprocessor = Preprocessor(file_content)
# text_chunks = preprocessor.text_chunks
