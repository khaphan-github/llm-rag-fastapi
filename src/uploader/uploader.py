import os
from abc import ABC, abstractmethod
from config.settings import settings

## This file handles logic for file upload from user then store to many data stores
## I want to apply SOLID principles to this file to make it more readable and maintainable
## First, I need logic to handle file upload with type text, docs, pdf, then save them to folder
## Second, I need logic to save file to MinIO storage, but this logic should be implemented later

class FileUploader(ABC):
    @abstractmethod
    def upload(self, file_path: str, file_content: bytes):
        pass

class LocalFileUploader(FileUploader):
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir

    def upload(self, file_path: str, file_content: bytes):
        try:
            if not os.path.exists(self.upload_dir):
                os.makedirs(self.upload_dir)
            file_name = os.path.basename(file_path)
            destination = os.path.join(self.upload_dir, file_name)
            
            # Save the uploaded file content
            with open(destination, 'wb') as dest_file:
                dest_file.write(file_content)
            
            print(f"File {file_name} uploaded to {self.upload_dir}")
        except PermissionError as e:
            print(f"Error: Permission denied while accessing {file_path} or {self.upload_dir}. {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

class MinioFileUploader(FileUploader):
    def __init__(self, minio_client, bucket_name: str):
        self.minio_client = minio_client
        self.bucket_name = bucket_name

    def upload(self, file_path: str, file_content: bytes):
        # This method will be implemented later
        pass