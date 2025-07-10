from helpers.config import get_settings, Settings
from typing import Any, Mapping

class BaseDataModel:

    def __init__(self, db_client: Mapping[str, Any]):
        self.db_client = db_client
        self.app_settings = get_settings()