import os
from abc import ABC, abstractmethod

## This file handles logic for reading file content from various sources
## I want to apply SOLID principles to this file to make it more readable and maintainable
## First, I need logic to handle reading file content with type text, docs, pdf from a folder
## Second, I need logic to read file content from MinIO storage, but this logic should be implemented later

class FileReader(ABC):
  @abstractmethod
  def read(self, file_path: str) -> bytes:
    pass

class FileConverter:
    def convert(self, file_content: bytes, file_type: str) -> str:
      if file_type == 'text':
        return file_content.decode('utf-8')
      elif file_type == 'md':
        return file_content.decode('utf-8')
      elif file_type == 'docs':
        # Placeholder for DOCX conversion logic
        return "DOCX content"
      elif file_type == 'pdf':
        # Placeholder for PDF conversion logic
        return "PDF content"
      else:
        raise ValueError(f"Unsupported file type: {file_type}")
      
class LocalFileReader(FileReader):
  def __init__(self, converter: FileConverter):
    self.converter = converter

  def read(self, file_path: str, file_type: str) -> str:
    try:
      full_path = os.path.join(file_path)
      print(full_path)
      if not os.path.exists(full_path):
        raise FileNotFoundError(f"File {file_path} not found in")
      
      with open(full_path, 'rb') as file:
        file_content = file.read()
      
      return self.converter.convert(file_content, file_type)
    except PermissionError as e:
      print(f"Error: Permission denied while accessing {file_path} or. {e}")
    except Exception as e:
      print(f"An unexpected error occurred: {e}")
      return ""
      
class MinioFileReader(FileReader):
  def __init__(self, minio_client, bucket_name: str):
    self.minio_client = minio_client
    self.bucket_name = bucket_name

  def read(self, file_path: str) -> bytes:
    # This method will be implemented later
    pass