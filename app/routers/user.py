from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
 # my created model, schemas etc 
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users", # router prefix
    tags=["User"] # this will seperate as group in API documentation
)

@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    # "sqlalchemy" style with ORM
    users = db.query(models.User).all()
    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if a user with this email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # create password hash 
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db:Session = Depends(get_db)):
    user_info = db.query(models.User).filter(models.User.id == id).first()
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not exists for id: {id}")
    return user_info