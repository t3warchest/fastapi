from .. import models, schemas, utils,oauth2
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import FastAPI,Response,status, HTTPException, Depends, APIRouter
from ..database import get_db 
from sqlalchemy.sql import func 

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

@router.get("/",response_model=List[schemas.PostWithVote])
def get_posts(db: Session = Depends(get_db), limit:int = 10,skip:int=0, search:Optional[str]="" ):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.name.contains(search)).limit(limit).offset(skip).all()
    print(posts)
    return posts


@router.get("/myposts",response_model = List[schemas.PostWithVote])
def get_my_posts(db : Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    my_posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.owner_id == current_user.id).all()
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


@router.post("/",status_code =status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate,db: Session = Depends(get_db), current_user:models.User = 
                 Depends(oauth2.get_current_user)):
    # cursor.execute(""" INSERT INTO posts (name,content,published) VALUES(%s,%s,%s) RETURNING *""",
    #                (post.name,post.content,post.published))
    # new_post = cursor.fetchone()
    # print(new_post)
    # conn.commit()
    
    
    
    
    # print(current_user.email)
    new_post = models.Post(**post.model_dump(),owner_id = current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


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