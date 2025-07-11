from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os 


class ProjectController(BaseController):
    """Controller for managing project-related operations, such as getting project paths."""
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        
        """Returns the path to the project directory, creating it if it does not exist."""

        project_dir = os.path.join(
            self.files_dir,
            project_id 
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir