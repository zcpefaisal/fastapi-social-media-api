# Python FastAPI Development - Comprehensive Course for Beginners
# https://www.youtube.com/watch?v=0sOvCWFmrtA
# FastAPI
# PostgreSql -> Database
# Pydantic -> widely used data validation library for Python
# psycopg2 -> PostgreSQL database adapter for Python
# SqlAlchemy -> open-source Python library that provides an SQL toolkit and ORM

import time
from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor

from sqlalchemy.orm import Session
 # my created model, schemas etc 
from . import models, schemas
from .database import engine, SessionLocal, get_db

app = FastAPI()

# for use "SQLAlchemy" and "postgres"/"mysql"/"any other", Must install DB driver like "psycopg2" here we use
# pip install SQLAlchemy==1.4

models.Base.metadata.create_all(bind=engine)



@app.get("/")
async def root():
    return {"message": "Hello Fast API !!"}

@app.get("/posts", response_model=List[schemas.PostResponse])
def get_all_posts(db: Session = Depends(get_db)):
    # "sqlalchemy" style with ORM
    posts = db.query(models.Post).all()
    return posts


# basic process 
# @app.post("/posts")

# standard process with detault status code response
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db)):
    # "sqlalchemy" style with ORM
    # new_post = models.Post(title=post.title, content=post.content)  #style-1
    new_post = models.Post(**post.dict()) #style-2 
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# please follow the path preceding
# /posts/latest  and  /posts/{id}  both are similar
# so follow the sequence

@app.get("/posts/latest", response_model=schemas.PostResponse)
def get_latest_post(db:Session = Depends(get_db)):
    # "sqlalchemy" style with ORM
    post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return post

@app.get("/posts/{id}", response_model=schemas.PostResponse)
def get_a_post(id: int, response: Response, db: Session=Depends(get_db)):
    # "sqlalchemy" style with ORM
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        # standard process 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id: {id}")

    return post



@app.put("/posts/{id}", response_model=schemas.PostResponse)
def update_posts(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # "sqlalchemy" style with ORM
    updated_post = db.query(models.Post).filter(models.Post.id == id)
    get_post = updated_post.first()
    if get_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    
    updated_post.update(post.dict())
    db.commit()
    return updated_post.first()


# standard process with detault status code response
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db:Session = Depends(get_db)):
    # "sqlalchemy" style with ORM
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    
    deleted_post.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)