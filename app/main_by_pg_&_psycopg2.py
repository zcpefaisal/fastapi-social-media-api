import time
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2 # সাইকো pg 2
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='password', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection successfully !!")
        break
    except Exception as error:
        print("Database connection faild")
        print(error)
        time.sleep(2)

@app.get("/")
async def root():
    return {"message": "Hello Fast API !!"}


my_post = [
    {
        "id": 1,
        "title": "This is first title",
        "content": "This is first content"
    },
    {
        "id": 2,
        "title": "This is second title",
        "content": "This is second title"
    }
]

def find_post(id):
    for p in my_post:
        if p['id'] == id:
            return p

def find_index(id):
    for i, p in enumerate(my_post):
        if p["id"] == id:
            return i


@app.get("/posts")
def get_all_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"date": posts}


# basic process 
# @app.post("/posts")

# standard process with detault status code response
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # new_post = post.dict()
    # new_post['id'] = randrange(1,100000)
    # my_post.append(new_post)
    cursor.execute("""INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING * """, (post.title, post.content))
    new_post = cursor.fetchone()
    conn.commit() #after commit then DB will impact
    return {"data": new_post}


# please follow the path preceding
# /posts/latest  and  /posts/{id}  both are similar
# so follow the sequence

@app.get("/posts/latest")
def get_latest_post():
    cursor.execute("""SELECT * FROM posts ORDER BY id DESC LIMIT 1 """)
    post = cursor.fetchone()
    # post = my_post[len(my_post)-1]
    return {"data": post}

@app.get("/posts/{id}")
def get_a_post(id: int, response: Response):
    # print(type(id)) id comes as string, so need to type custing / type hint in param for validation
    # post = find_post(id)

    cursor.execute("""SELECT * FROM posts WHERE id=%s """, (id,))
    post =  cursor.fetchone()
    if not post:
        # standard process 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id: {id}")

        # old process 
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post not found for id: {id}"} 

    return {"data": post}



@app.put("/posts/{id}")
def update_posts(id: int, post: Post):
    # index = find_index(id)
    # print(index)
    cursor.execute("""UPDATE posts SET title=%s, content=%s WHERE id=%s RETURNING *""", (post.title, post.content, id))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    
    return {'data': updated_post}


# standard process with detault status code response
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):
    # index = find_index(id)
    # print(index)
    cursor.execute("""DELETE FROM posts WHERE id=%s""", (id,))
    deleted_post = cursor.rowcount
    # print(deleted_post)
    conn.commit()
    # Check the rowcount to see how many rows were affected by the DELETE command.
    # If no rows were deleted (rowcount is 0), the post didn't exist.
    if deleted_post == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found for id {id}")
    # my_post.pop(deleted_post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)