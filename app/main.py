from . import model, schemas
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
import time
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor

model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


while True:
    try:
        conn = psycopg2.connect(host='localhost',database='postgres',user="postgres",password='1234',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connected")
        break
    except Exception as error:
        print("Database is not connected")
        print("Error : ", error)
        time.sleep(5)


app = FastAPI()


    
   

post1 = [{
         "title":"Penguin",
          "content":"Life of Penguin",
          "Published": True,
          "rating": 4,
          "id": 67
          }]

def find_post(id):
    for i in post1:
        if i["id"] == id:
            return i

def find_index(id):
    for i,p in enumerate(post1):
        if p["id"] == id:
            return i


@app.get("/")
def view_posts():
    try:
        cursor.execute('SELECT * FROM posts')
        post = cursor.fetchall()
        if not post:
            return {"message":"No post available"}
        return { "message":post}
    except Exception as e:
        conn.rollback() 
        raise e


@app.post("/create_post", status_code=status.HTTP_201_CREATED, response_model=schemas.RespPost)
def create_posts(post: schemas.CreatePost, db: Session = Depends(get_db)):
    try:
        new_posts = model.Post(**post.dict())
        db.add(new_posts)
        db.commit()
        db.refresh(new_posts)
        return new_posts
    except Exception as e:
        db.rollback()   
        raise e
    
@app.get("/get_post/{id}")
def get_posts(id: int, response : Response, db: Session = Depends(get_db), response_model=schemas.RespPost):
    post = db.query(model.Post).filter(model.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found!")
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"message": f"post with id {id} was not found"}
    return post


@app.delete("/delete_post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db)):
    post = db.query(model.Post).filter(model.Post.id == id)
    
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found!")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/update_post/{id}")
def update_post(id: int, post: schemas.CreatePost, db: Session = Depends(get_db), response_model=schemas.RespPost):
    posts_query = db.query(model.Post).filter(model.Post.id == id)
    posts = posts_query.first()
    
    if posts == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found!")
    posts_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return posts_query.first()
