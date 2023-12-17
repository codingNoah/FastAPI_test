from pydantic import BaseModel
from typing import List

class Blog(BaseModel):
    title: str
    body: str 
    userId: str

class User(BaseModel):
    username: str
    password: str 

class GenericBlog(BaseModel):
    title: str
    body: str 

class ShowUser(BaseModel):
    username: str
    blogs: List[GenericBlog]

class User(BaseModel):
    username: str

class ShowBlog(BaseModel):
    title: str
    body: str
    creator: User

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


