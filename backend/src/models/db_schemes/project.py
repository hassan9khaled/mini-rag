from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId


class Project(BaseModel):
    
    """Project Scheme representing a project in the application."""

    id: Optional[ObjectId] = Field(None, alias="_id")
    project_name: str = Field(..., min_length=1)

    @field_validator('project_name')
    def validate_project_name(cls, value):
        if not value:
            raise ValueError("project_name is not correct")
        
        return value
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):

        return [
            {
                "key": [
                    ("project_name", 1)
                ],
                "name": "project_name_index_1",
                "unique": True
            }
        ]