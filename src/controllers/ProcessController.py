from .BaseController import BaseController
from .ProjectController import ProjectController
from helpers.config import get_settings

from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from models import ProcessingEnum

import os
import re
import csv


class ProcessController(BaseController):
    """Controller for processing files in a project, including loading and splitting file content."""
    def __init__(self, project_name: str):
        super().__init__()

        self.project_name = project_name
        self.project_path = ProjectController().get_project_path(project_name)
        self.max_records_exceeded = False
        self.csv_file_max_records = get_settings().CSV_FILE_MAX_RECORDS

    def get_file_extension(self, file_id: str):
        """Returns the file extension of the given file ID."""

        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self, file_id: str):
        """Returns the appropriate file loader for the given file ID."""

        # Determine the file extension
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )
        # Check if the file exists
        if not os.path.exists(file_path):
            return None
        
        # Return the appropriate loader based on the file extension
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        if file_ext == ProcessingEnum.CSV.value:
            return CSVLoader(file_path)
        
        return None

    
    def get_file_content(self, file_id: str):
        """Loads the content of the file using the appropriate loader."""

        # Get the file loader
        loader = self.get_file_loader(file_id=file_id)

        if loader:
            return loader.load()

        return None
    

    

    def process_file_content(self, file_content: list, file_id: str,
                             chunk_size: int=300, overlap_size: int=50):
        
        """Processes the file content by splitting it into chunks."""
        
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            separators=["\n\n", "\n", ".", "؟", "!", " "],
            length_function=len,
        )



        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]


        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
        )

        return chunks, self.max_records_exceeded