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




# test alchemy connection 
# if connect successfuly then create table based on model define
@app.get("/testalchemy")
def testalchemy(db: Session = Depends(get_db)):
    return {"status": "success"}



# pydantic model for validation request
# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True
#     # rating: Optional[int] = None

# "postgres" connection by "psycopg2" adapter 
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='password', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection successfully !!")
#         break
#     except Exception as error:
#         print("Database connection faild")
#         print(error)
#         time.sleep(2)

@app.get("/")
async def root():
    return {"message": "Hello Fast API !!"}

# manual data object for example
# my_post = [
#     {
#         "id": 1,
#         "title": "This is first title",
#         "content": "This is first content"
#     },
#     {
#         "id": 2,
#         "title": "This is second title",
#         "content": "This is second title"
#     }
# ]

# manualy data find from dict
# def find_post(id):
#     for p in my_post:
#         if p['id'] == id:
#             return p

# manually index find for a data
# def find_index(id):
#     for i, p in enumerate(my_post):
#         if p["id"] == id:
#             return i


@app.get("/posts", response_model=List[schemas.PostResponse])
def get_all_posts(db: Session = Depends(get_db)):
    # "psycopg2" style with raw query 
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    # "sqlalchemy" style with ORM
    posts = db.query(models.Post).all()
    return posts


# basic process 
# @app.post("/posts")

# standard process with detault status code response
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db)):
    # new_post = post.dict()
    # new_post['id'] = randrange(1,100000)
    # my_post.append(new_post)

    # "psycopg2" style with raw query 
    # cursor.execute("""INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING * """, (post.title, post.content))
    # new_post = cursor.fetchone()
    # conn.commit() #after commit then DB will impact

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
    # "psycopg2" style with raw query 
    # cursor.execute("""SELECT * FROM posts ORDER BY id DESC LIMIT 1 """)
    # post = cursor.fetchone()
    # post = my_post[len(my_post)-1]

    # "sqlalchemy" style with ORM
    post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return post

@app.get("/posts/{id}", response_model=schemas.PostResponse)
def get_a_post(id: int, response: Response, db: Session=Depends(get_db)):
    # print(type(id)) id comes as string, so need to type custing / type hint in param for validation
    # post = find_post(id)
    
    # "psycopg2" style with raw query 
    # cursor.execute("""SELECT * FROM posts WHERE id=%s """, (id,))
    # post =  cursor.fetchone()

    # "sqlalchemy" style with ORM
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        # standard process 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id: {id}")

        # old process 
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post not found for id: {id}"} 

    return post



@app.put("/posts/{id}", response_model=schemas.PostResponse)
def update_posts(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # index = find_index(id)
    # print(index)

    # "psycopg2" style with raw query 
    # cursor.execute("""UPDATE posts SET title=%s, content=%s WHERE id=%s RETURNING *""", (post.title, post.content, id))
    # updated_post = cursor.fetchone()
    # conn.commit()

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
    # index = find_index(id)
    # print(index)

    # "psycopg2" style with raw query 
    # cursor.execute("""DELETE FROM posts WHERE id=%s""", (id,))
    # deleted_post = cursor.rowcount
    # # print(deleted_post)
    # conn.commit()
    # Check the rowcount to see how many rows were affected by the DELETE command.
    # If no rows were deleted (rowcount is 0), the post didn't exist.
    # if deleted_post == 0:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    # my_post.pop(deleted_post)

    # "sqlalchemy" style with ORM
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    
    deleted_post.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)