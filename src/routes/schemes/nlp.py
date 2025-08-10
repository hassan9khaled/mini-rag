from typing import List, Optional
from pydantic import BaseModel

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0
    asset_name: str

class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 5
    assets: List[str]