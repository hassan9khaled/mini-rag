from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os 
import shutil

class ProjectController(BaseController):
    """Controller for managing project-related operations, such as getting project paths."""
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_name: str):
        
        """Returns the path to the project directory, creating it if it does not exist."""

        project_dir = os.path.join(
            self.files_dir,
            project_name 
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir
    
    def delete_project(self, project_name):
        

        _ = shutil.rmtree(self.get_project_path(project_name=project_name), ignore_errors=True)

        return True