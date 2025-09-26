# pydantic model for validation request
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


# also we can use schema validation class differently 
# for example for the create post we can use PostCreate
# also for the update post we can use PostUpdate and so on
# or we can use single one
class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime

    # sqlalchemy response the alchemy model so pidantic does not understand __pydantic_post_init
    # but pidantic work with dictionary dict, thats why need to active the orm mode for validation
    class Config:
        from_attributes = True



class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_active: bool = True

    class Config:
        from_arrtibutes = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None