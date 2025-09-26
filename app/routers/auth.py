from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2


router = APIRouter(tags=['Authantication'])

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # OAuth2PasswordRequestForm will work on username field not the email field
    # Also note that now request with raw-> json will not work, need to pass from-data 
    # {
    #     "username": "test3@faisalalam.me",
    #     "password": "123456"
    # }
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credential")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credential")
    
    # create a token
    access_token = oauth2.create_access_token(data = {"user": user.id, "email": user.email})
    # return token
    return {"access_token": access_token, "token_type": "bearer"}