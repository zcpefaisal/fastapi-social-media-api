# pydantic model for validation request
from datetime import datetime
from pydantic import BaseModel

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