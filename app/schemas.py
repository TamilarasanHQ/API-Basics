from pydantic import BaseModel
from datetime import datetime
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    

class CreatePost(Post):
    pass

class RespPost(Post):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
