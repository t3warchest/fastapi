from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint

class PostBase(BaseModel):
    name : str
    content : str
    published : bool = True

class PostCreate(PostBase):
    pass

class UserResponse(BaseModel):
    id : int
    email :EmailStr
    created_at : datetime
    
    class Config:
        orm_mode = True

class PostResponse(PostBase):
    id : int
    created_at : datetime
    owner_id : int
    owner : UserResponse
    
    class Config:
        orm_mode = True

class PostWithVote(BaseModel):
    Post:PostResponse
    votes:int
    
    class Config:
        orm_mode = True

class User(BaseModel):
    email : EmailStr
    password : str



class UserLogin(BaseModel):
    email : EmailStr
    password : str
    
class AccessToken(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    id : Optional[int] = None

class Vote(BaseModel):
    post_id : int
    dir : conint(le=1)