from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

class Asset(BaseModel):

    """Asset Scheme representing a file or resource in a project."""

    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: dict = Field(default=None)
    source: str = Field(..., min_length=1)
    created_at: datetime = Field(default=datetime.now(timezone.utc))

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
    
    @classmethod
    def get_indexes(cls):

        """Returns the indexes for the Asset collection."""

        return [
            {
                "key": [
                    ("asset_project_id", 1)
                ],
                "name": "asset_project_id_index_1",
                "unique": False
            },
            {
                "key": [
                    ("asset_project_id", 1),
                    ("asset_name", 1)
                ],
                "name": "asset_project_id_name_index_1",
                "unique": True
            }
        ]
