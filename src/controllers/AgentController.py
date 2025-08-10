from .BaseController import BaseController
from .ProjectController import ProjectController
from helpers.config import get_settings
import logging
logger = logging.getLogger('uvicorn.error')

import requests

class AgentController(BaseController):
    def __init__(self):
        super().__init__()

        self.app_name = "software_team"
        self.session_id = "session_001"
        self.user_id = "user"
        self.base_url = "http://localhost:8000"

    def create_session(self):
        
        res = requests.post(f'{self.base_url}/apps/{self.app_name}/users/{self.app_name}/sessions/{self.session_id}')

    def run(self, asset, prompt):

        url = f"{self.base_url}/run"

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "app_name": "software_team",
            "user_id": self.user_id,
            "session_id": self.session_id,
            "new_message": {
                "role": "user",
                "parts": [
                    {"text": f"{asset} for this data set, {prompt}"}
                ]
            }
        }

        response = requests.post(url, json=data, headers=headers)

        try:
            return True
        except Exception as e:
            logger.error(f"Error while sending message: {e}")
            return False
        

    def get_session_info(self):

        session_url = f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions/{self.session_id}"
        session_response = requests.get(session_url)
        session_data = session_response.json()
        agent_response = session_data["state"]["agent_response"]

        return agent_response
    
    def get_session_id(self):
        
        sessions_url = f"{self.base_url}/apps/{self.app_name}/users/{self.user_id}/sessions"
        sessions_response = requests.get(sessions_url)
        session_id = sessions_response.json()[0].get("id")

        self.session_id = session_id

        return True
