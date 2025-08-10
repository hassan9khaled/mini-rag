from .BaseController import BaseController
from models.db_schemes import Project, Data_Chunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json, re
from helpers.config import get_settings
from models.db_schemes import RetrievedDocument

class NLPController(BaseController):
    
    def __init__(self, vectordb_client, embedding_client,
                  generation_client, template_parser):
        
        super().__init__()

        self.generation_client = generation_client
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

        self.settings = get_settings()

    def create_collection_name(self, project_name: str):
        return f"collection_{project_name}".strip()

    def reset_vector_db_collection(self, project: Project):

        collection_name = self.create_collection_name(project_name=project.project_name)

        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_name=project.project_name)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_into_vector_db(self, project: Project, chunks: List[Data_Chunk],
                             chunks_ids: List[int],
                             do_reset: bool = False):
        
        # Step 1: create collection name
        collection_name = self.create_collection_name(project_name = project.project_name)

        # Step 2: manage the items
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(text=text,
                                             document_type = DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        # Step 3: create collection if not exists

        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size = self.embedding_client.embedding_size,
            do_reset = do_reset
        )


        # Step 4: insert into the database

        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids
        )

        return True
    
    def search_vector_db_collection(self, project: Project, text: str, assets: List[str], limit: int = 5):
        
        # step 1: get the collection name
        collection_name = self.create_collection_name(project_name = project.project_name)

        # step 2: get text embedding vector
        vector = self.embedding_client.embed_text(
            text = text,
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vector or len(vector) == 0:
            return False
        


        # step 3: do semantic search

        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit,
            assets=assets
        )

        if not results:

            return False

        return results
    
    def answer_rag_question(self, project: Project, query: str, assets: List[str], limit: int = 5):

        if "qwen" in self.settings.GENERATION_MODEL_ID:
            query = "/no_think" + query

        answer, full_prompt, chat_history = None, None, None

        # step 1: retreive related document
        
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
            assets=assets
        )
        

        if not retrieved_documents or len(retrieved_documents) == 0:

            return answer, full_prompt, chat_history
        
        # step 2: construct LLM prompt
       
        system_prompt = self.template_parser.get("rag", "system_prompt")

        user_query = self.template_parser.get("rag", "user_query", {"query":query})

        documents_prompts = "\n".join([

             self.template_parser.get("rag", "document_prompt", {
                 "doc_num": idx + 1,
                 "chunk_text": doc.text
             })

             for idx, doc in enumerate(retrieved_documents) 
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt")

        chat_history = [
            self.generation_client.construct_prompt(
                prompt = system_prompt,
                role = self.generation_client.enums.SYSTEM.value

            )
        ]

        full_prompt = "\n\n".join([user_query, documents_prompts, footer_prompt])

        answer = self.generation_client.generate_text(
            prompt = full_prompt,
            chat_history = chat_history
        )

        pattern = r"(?s)<[^>]+>|^\s*$"

        answer = re.sub(pattern, "", answer).strip()

        return answer, full_prompt, chat_history

    def list_all_projects(self):

        return json.loads(
            json.dumps(self.vectordb_client.list_all_collections(), default=lambda x: x.__dict__)
        )