from pydantic import BaseModel, Field, field_validator
from bson.objectid import ObjectId
from typing import Optional

class Data_Chunk(BaseModel):

    """Data Chunk Scheme representing a chunk of text data in a project."""

    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True

    
    @classmethod
    def get_indexes(cls):
        
        """Returns the indexes for the Data Chunk collection."""

        return [
            {
                "key": [
                    ("chunk_project_id", 1)
                ],
                "name": "chunk_project_id_inedx_1",
                "unique": False # usually the chunks has the same project_id
            }
        ]
    
class RetrievedDocument(BaseModel):
    id: int
    text: str
    score: float
    source: str
    page: Optional[int] = None