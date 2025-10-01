from typing import List # Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import oauth2

 # my created model, schemas etc 
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/posts", # router prefix
    tags=["Post"] # this will seperate as group in API documentation
)

# @router.get("/", response_model=List[schemas.PostResponse])
@router.get("/", response_model=List[schemas.PostWithVote])
def get_all_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, page: int = 0, search: str = ""):
    # "sqlalchemy" style with ORM
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(page).all()

    posts_with_vote_count = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(page).all()
    return posts_with_vote_count


# basic process 
# @router.post("/")

# standard process with detault status code response
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # "sqlalchemy" style with ORM
    # new_post = models.Post(title=post.title, content=post.content)  #style-1
    # print(current_user)
    new_post = models.Post(user_id = current_user.id, **post.dict()) #style-2 
    # new_post.user_id = current_user.id
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# please follow the path preceding
# /latest  and  /{id}  both are similar
# so follow the sequence

@router.get("/latest", response_model=schemas.PostWithVote)
def get_latest_post(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # "sqlalchemy" style with ORM
    # post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    post_with_vote_count = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).order_by(models.Post.id.desc()).first()
    return post_with_vote_count

@router.get("/{id}", response_model=schemas.PostWithVote)
def get_a_post(id: int, response: Response, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # "sqlalchemy" style with ORM
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post_with_vote_count = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post_with_vote_count:
        # standard process 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id: {id}")

    return post_with_vote_count



@router.put("/{id}", response_model=schemas.PostResponse)
def update_posts(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # "sqlalchemy" style with ORM
    updated_post = db.query(models.Post).filter(models.Post.id == id)
    get_post = updated_post.first()
    if get_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    
    if get_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unauthorized to perform the request")
    
    updated_post.update(post.dict())
    db.commit()
    return updated_post.first()


# standard process with detault status code response
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # "sqlalchemy" style with ORM
    deleted_post_query = db.query(models.Post).filter(models.Post.id == id)
    
    deleted_post = deleted_post_query.first()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    
    if deleted_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unauthorized to perform the request")
    
    deleted_post_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
