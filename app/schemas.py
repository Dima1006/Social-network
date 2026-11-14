from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Annotated


class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_mode = True



class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass



class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        from_mode = True

class PostOut(BaseModel):
    Post: PostResponse  # Вложенная модель поста
    votes: int          # Количество голосов

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str





class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(le=1)]