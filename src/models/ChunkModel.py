from .BaseDataModel import BaseDataModel
from .db_schemes import Data_Chunk
from .enums.DataBaseEnum import DataBaseEnum
from typing import Any, Mapping
from bson.objectid import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client: Mapping[str, Any]):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: Data_Chunk):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_unset=True))
        chunk._id = result.inserted_id

        return chunk
    
    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if result in None:
            return None
        
        return Data_Chunk(**result)
    

    async def insert_many_chunks(self, chunks: list, batch_size: int=200):
        
        for i in range(0, len(chunks), batch_size):

            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

            return len(chunks)
        

    async def delete_chunks_by_project_id(self, project_id: ObjectId):

        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count