# FastAPI
# PostgreSql -> Database
# Pydantic -> widely used data validation library for Python
# psycopg2 -> PostgreSQL database adapter for Python
# SqlAlchemy -> open-source Python library that provides an SQL toolkit and ORM

# import time
# from typing import List, Optional
from fastapi import FastAPI # , Response, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.params import Body
# from pydantic import BaseModel
# from random import randrange
# import psycopg2
# from psycopg2.extras import RealDictCursor

# from sqlalchemy.orm import Session
 # my created model, schemas etc 
# from . import models
# from .database import engine # get_db, SessionLocal
from .routers import post, user, auth, vote

app = FastAPI()

origins = [
    # "*" this * will allow all the domain incoming request
    "https://www.google.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# for use "SQLAlchemy" and "postgres"/"mysql"/"any other", Must install DB driver like "psycopg2" here we use
# pip install SQLAlchemy==1.4

# this line disable for implement alembic, 
# so that alchemy will connect by alembic, not the direct connect
# models.Base.metadata.create_all(bind=engine)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
async def root():
    return {"message": "Hello Fast API !!"}


