from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from typing import Any, Mapping

class ProjectModel(BaseDataModel):
    """
    Model for managing project-related database operations.

    This class provides an interface for interacting with the projects collection in the database.
    It includes methods for creating, retrieving, and managing projects.
    """

    def __init__(self, db_client: Mapping[str, Any]):
        """
        Initializes the ProjectModel.

        Args:
            db_client (Mapping[str, Any]): The database client instance.
        """
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: Mapping[str, Any]):
        """
        Creates an instance of ProjectModel and initializes the collection.

        This factory method ensures that the collection and its indexes are created
        before the model instance is returned.

        Args:
            db_client (Mapping[str, Any]): The database client instance.

        Returns:
            ProjectModel: An instance of the ProjectModel.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        """
        Initializes the project collection in the database.

        Checks if the collection already exists. If not, it creates the collection
        and defines its indexes for efficient querying.
        """
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            
            # Create indexes for the collection
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_project(self, project: Project):
        """
        Creates a new project in the database.

        Args:
            project (Project): The project object to be created.

        Returns:
            Project: The created project object, including its new database ID.
        """
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        return project
    
    async def get_project_or_create_one(self, project_id: str):
        """
        Retrieves a project by its ID or creates a new one if it doesn't exist.

        Args:
            project_id (str): The ID of the project to retrieve or create.

        Returns:
            Project: The retrieved or newly created project object.
        """
        record = await self.collection.find_one({
            "project_id": project_id
        })

        if record is None:
            # Create a new project if no record is found
            project = Project(project_id=project_id) # type: ignore
            project = await self.create_project(project=project)
            return project
        
        return Project(**record)
            
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        """
        Retrieves a paginated list of all projects.

        Args:
            page (int, optional): The page number to retrieve. Defaults to 1.
            page_size (int, optional): The number of projects per page. Defaults to 10.

        Returns:
            tuple[list[Project], int]: A tuple containing the list of projects and the total number of pages.
        """
        # Count the total number of documents for pagination
        total_documents = await self.collection.count_documents({})

        # Calculate the total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        # Retrieve the projects for the current page
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []

        async for document in cursor:
            projects.append(
                Project(**document)
            )

        return projects, total_pages