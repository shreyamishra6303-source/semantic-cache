from pydantic import BaseModel,EmailStr,Field
from datetime import datetime
from typing import Optional,List

class Messages(BaseModel):
    role:str
    content:str

class completionMessage(BaseModel):
    model:str
    messages:List[Messages]
    temperature:Optional[float]=0.7