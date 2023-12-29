from .. import models, schemas, utils,oauth2
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import FastAPI,Response,status, HTTPException, Depends, APIRouter
from ..database import get_db 
from sqlalchemy.sql import func,desc
from sqlalchemy import ARRAY
import psycopg2
from psycopg2.extras import RealDictCursor
import time
router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

while True:
    try:
        conn = psycopg2.connect(host = "localhost", database='fastapi', user='postgres',
                                password='password123', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("sucess")
        break
    except Exception as error:
        print("connection failed")
        print("Error",error)
        time.sleep(2)

@router.get("/",response_model=List[schemas.PostWithVote])
def get_posts(db: Session = Depends(get_db),current_user:models.User = 
                 Depends(oauth2.get_current_user), limit:int = 5, skip:int = 0, search:Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).all()
    
    no_of_seen_posts = db.query(models.Test).filter(models.Test.user_id == current_user.id).count()
    total_posts = db.query(models.Post).count()
    new_limit = (no_of_seen_posts+limit) - total_posts
    new_limit = new_limit if new_limit>0 else limit
    print(new_limit)
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.id.not_in(db.query(models.Test.seen_posts).filter(models.Test.user_id == current_user.id))
                                   ,models.Post.name.contains(search),models.Post.published==True).order_by(
                desc("votes"),desc(models.Post.created_at)).limit(limit).offset(skip)
    
    remaining_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.name.contains(search),models.Post.published==True).order_by(
                desc("votes"),desc(models.Post.created_at)).limit(new_limit).offset(skip)
    final_post = posts.union_all(remaining_post)
    to_be_returned = final_post.all()
    
    post_ids = db.query(models.Post.id, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.id.not_in(db.query(models.Test.seen_posts).filter(models.Test.user_id == current_user.id))
                ,models.Post.name.contains(search),models.Post.published==True).order_by(
                desc("votes"),desc(models.Post.created_at)).limit(limit).offset(skip).all()
    
    print(post_ids)
    get_user = db.query(models.Test).filter(models.Test.user_id == current_user.id)
    
    # if not get_user.first():
    #     post_ids_array = []
    #     for (id,count) in post_ids:
    #         post_ids_array.append(id)
    posts_seen_by_user = db.query(models.Test.seen_posts).filter(models.Test.user_id == current_user.id).all()
    for (post_id,count) in post_ids:
        if (post_id,) not in posts_seen_by_user: 
            new_entry = models.Test(seen_posts = post_id,user_id = current_user.id)
            db.add(new_entry)
    db.commit()
    # else:
    #     (seen_posts_py,) = db.query(models.Test.seen_posts).filter(models.Test.user_id == current_user.id).first()
    #     print(seen_posts_py)
    #     for (id,count) in post_ids:
    #         if id not in seen_posts_py:
    #             cursor.execute("""UPDATE test
    #                             SET seen_posts = ARRAY_APPEND(seen_posts,%s)
    #                             WHERE user_id = %s""",(id,current_user.id))
    #     conn.commit()
    # (seen_post_ids_array,) = db.query(models.Test.seen_posts).filter(models.Test.user_id == current_user.id)
    # updated_limit = limit - len(seen_post_ids_array) if limit >= len(seen_post_ids_array) else 0
    # print(posts)
    
    return to_be_returned


@router.get("/myposts",response_model = List[schemas.PostWithVote])
def get_my_posts(db : Session = Depends(get_db), current_user = Depends(oauth2.get_current_user), limit:int = 5,skip:int = 0,search:Optional[str] = ""):
    my_posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.name.contains(search),models.Post.published==True).order_by(
                desc("votes"),desc(models.Post.created_at)).limit(limit).offset(skip)
    return my_posts 

@router.get('/{id}') 
def get_post(id: int, response : Response,db: Session = Depends(get_db)) -> schemas.PostWithVote:
    # cursor.execute("""SELECT * FROM posts WHERE id =%s""",(id,))
    # cur_post = cursor.fetchone()
    # cur_post = db.query(models.Post).filter(models.Post.id == id).first()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.id == id).first()
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No post with id {id}")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message":f"No post with id {id}"}
    
    
    return posts


@router.post("/",status_code =status.HTTP_201_CREATED,response_model=schemas.PostResponse) #, response_model=schemas.PostResponse
def create_posts(posts: schemas.PostCreate,db: Session = Depends(get_db), current_user:models.User = 
                 Depends(oauth2.get_current_user)): # change posts: List[schemas.PostCreate] to post:schemas.PostCreate
    
    # cursor.execute(""" INSERT INTO posts (name,content,published) VALUES(%s,%s,%s) RETURNING *""",
    #                (post.name,post.content,post.published))
    # new_post = cursor.fetchone()
    # print(new_post)
    # conn.commit()
    
     #remove for loop 
    new_post = models.Post(**posts.model_dump(),owner_id = current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post#return new_post


@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id : int, db: Session = Depends(get_db), current_user:models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(id,))
    # post_id = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No post with id {id}")
    
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorised acccess")
    
    post.delete(synchronize_session = False)
    db.commit()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_post(id : int, post : schemas.PostCreate, db : Session = Depends(get_db),
                current_user:models.User = Depends(oauth2.get_current_user)) -> schemas.PostResponse:
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title,post.content,post.published,id))
    # upd_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == id) #just sqving the query SELECT posts.id AS posts_id, posts.name AS posts_name, posts.content AS posts_content, posts.published AS posts_published, posts.created_at AS posts_created_at FROM posts WHERE posts.id = %(id_1)s
    post_db = post_query.first()
    if not post_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No post with id {id}")
    
    if post_db.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorised acccess")
    
    post_query.update(post.model_dump(),synchronize_session=False)  #post->post_db becuyase interfering with post in path param
    # post_db = post_query.first()
    db.commit()
    return post_query.first() #check why using post_db shows nothing