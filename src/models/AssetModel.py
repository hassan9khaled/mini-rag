from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from typing import Any, Mapping
from bson import ObjectId

class AssetModel(BaseDataModel):

    """Model for managing asset-related database operations."""

    def __init__(self, db_client: Mapping[str, Any]):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]


    @classmethod
    async def create_instance(cls, db_client: Mapping[str, Any]):
        """Creates an instance of AssetModel and initializes the collection."""

        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):

        """Initializes the asset collection and creates indexes if not already present."""
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            
            # Create indexes for the asset collection
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )
    
    async def create_asset(self, asset: Asset):
        """Inserts a new asset into the collection and returns the asset with its ID."""
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id

        return asset
    
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        """Retrieves all assets for a given project and asset type."""
        records = await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type
        }).to_list(length=None)

        return [
            Asset(**record)
            for record in records
        ]
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        """Retrieves a specific asset record by project ID and asset name."""

        # Find the asset record in the collection
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name,            
        })

        if record:
            return Asset(**record)
        else:
            return None