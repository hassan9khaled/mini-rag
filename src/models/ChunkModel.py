from .BaseDataModel import BaseDataModel
from .db_schemes import Data_Chunk
from .enums.DataBaseEnum import DataBaseEnum
from typing import Any, Mapping
from bson.objectid import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):

    """Model for managing chunk-related database operations."""
    
    def __init__(self, db_client: Mapping[str, Any]):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]


    @classmethod
    async def create_instance(cls, db_client: Mapping[str, Any]):
        """Create an instance of ChunkModel and initialize the collection."""

        instance = cls(db_client)
        await instance.init_collection()
        return instance
    

    async def init_collection(self):
        """Initialize the collection and create indexes if they do not exist."""

        # Check if the collection exists, if not create it
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:

            # Create the collection
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = Data_Chunk.get_indexes()
            
            # Create indexes if they do not exist
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_chunk(self, chunk: Data_Chunk):

        """Insert a new chunk into the database."""

        # Insert the chunk into the collection
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_unset=True))
        chunk.id = result.inserted_id

        return chunk
    
    async def get_chunk(self, chunk_id: str):
        """Retrieve a chunk by its ID."""

        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if result in None:
            return None
        
        return Data_Chunk(**result)
    

    async def insert_many_chunks(self, chunks: list, batch_size: int=200):

        """Insert multiple chunks into the database in batches."""
        for i in range(0, len(chunks), batch_size):

            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

            return len(chunks)
        

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        
        """Delete all chunks associated with a specific project ID."""

        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count