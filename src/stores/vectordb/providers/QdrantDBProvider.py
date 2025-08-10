from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from typing import List
from models.db_schemes import RetrievedDocument

import logging

class QdrantDBProvider(VectorDBInterface):
    
    def __init__(self, db_path: str, distance_method: str):
        
        self.client = None
        self.distance_method = None
        self.db_path = db_path

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_exists(self, collection_name) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def search_by_vector(self, collection_name, vector, assets, limit=5):

        
        results =  self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchAny(
                            any=assets
                        )
                    )
                ]

            ),
            limit=limit,
            with_payload=True,
            with_vectors=True
        )

        if not results or len(results) == 0:
            return None
        
        return [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload["text"],
                "id": result.id,
                "source": result.payload["metadata"]["source"],
                # "page": result.payload["metadata"]["page"]
            })

            for result in results
        ]

    def get_collection_info(self, collection_name) -> dict:               
        return self.client.get_collection(collection_name=collection_name)
    
    def insert_one(self, collection_name, text, vector, metadata = None, record_id = None):
        
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"`{collection_name}` collection is not found, can't insert a new record")
            return False
        
        try:

            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id = [record_id],
                        vector=vector,
                        payload={'text': text, 'metadata': metadata}
                    )
                ]
            )

        except  Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True


    def insert_many(self, collection_name, texts, vectors,
                     metadata = None, record_ids = None, batch_size = 50):
        
        if metadata is None:
            metadata = [None] * len(texts)
        
        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_record_ids =  record_ids[i:batch_end]

            batch_records = [
                models.Record(
                    id = batch_record_ids[rec],
                    vector=batch_vectors[rec],
                    payload={"text": batch_texts[rec], "metadata": batch_metadata[rec]}
                )

                for rec in range(len(batch_texts))
            ]
            

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except  Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

            return True

    def delete_collection(self, collection_name):
        if self.is_collection_exists(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name, embedding_size, do_reset = False):

        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_exists(collection_name=collection_name):
            _ = self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size = embedding_size,
                        distance = self.distance_method
                    )
                )
            
            return True
        
        return False