from typing import List
from fastapi import FastAPI,Response,status, HTTPException, Depends, APIRouter 
from .. import database,schemas,models,oauth2
from sqlalchemy.orm import Session 
import redis 
import json

rd = redis.Redis("localhost",port=6379,db=0)

router = APIRouter(
    prefix="/comment",
    tags=['comment']
)

@router.get('/{post_id}',response_model=List[schemas.CommentGetResponse])
def get_comment(post_id:int,db:Session = Depends(database.get_db)):
    
    cached_data = rd.get(post_id)
    if cached_data:
        print("hit")
        return json.loads(cached_data)
    else:
        print("miss")
        comments = db.query(models.Comment.comment,models.Comment.commenter_id,models.Comment.created_at).filter(
            models.Comment.post_id == post_id)
        comment_rows = comments.all()
        my_dict = {}
        cols = comments.column_descriptions
        
        comments_list = []
        for i in range(len(comments.all())):
            my_dict = {}
            for idx in range(3):
                my_dict[cols[idx]['name']] = comment_rows[i][idx]
            
            comments_list.append(my_dict)
        
        a = json.dumps(comments_list,default=str)
        
        rd.set(post_id,a)
        
    
    return comments.all()

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.CommentResponse)
def post_comment(comment:schemas.Comment, current_user:models.User = Depends(oauth2.get_current_user),db:Session = Depends(database.get_db)):
    
    post_query = db.query(models.Post).filter(models.Post.id == comment.post_id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No post with id {comment.post_id}")
    
    comment_query = db.query(models.Comment).filter(models.Comment.post_id == comment.post_id, models.Comment.commenter_id == current_user.id)
    found_vote = comment_query.first()
    
    if found_vote:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"user already commented on {comment.post_id}")
    if rd.exists(post.id):
        rd.delete(post.id)
    
    new_comment = models.Comment(**comment.model_dump(),commenter_id = current_user.id)
    db.add(new_comment)
    db.commit()
    
    final_post = db.query(models.Post.name,models.Post.content,models.Post.owner_id,models.Comment.created_at,models.Comment.comment,models.Comment.commenter_id).join(models.Comment,models.Post.id == models.Comment.post_id).filter(models.Comment.commenter_id == current_user.id).first()
    return final_post

@router.put('/{id}',response_model = schemas.CommentResponse)
def update_comment(id:int,comment:schemas.Comment,db:Session = Depends(database.get_db),
                   current_user:models.User = Depends(oauth2.get_current_user)):
    
    comment_query = db.query(models.Comment).filter(models.Comment.comment_id == id) 
    comment_db = comment_query.first()
    if not comment_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No comment with id {id}")
    
    if comment_db.commenter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorised acccess")
    
    if rd.exists(id):
        rd.delete(id)
    
    comment_query.update(comment.model_dump() ,synchronize_session=False)
    db.commit()
    final_post = db.query(models.Post.name,models.Post.content,models.Post.owner_id,models.Comment.created_at,models.Comment.comment,models.Comment.commenter_id).join(models.Comment,models.Post.id == models.Comment.post_id).filter(models.Post.id == comment.post_id).first()
    return final_post

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id : int, db: Session = Depends(database.get_db), current_user:models.User = Depends(oauth2.get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.comment_id == id)
    if comment.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No comment with id {id}")
    
    if comment.first().commenter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="unauthorised acccess")
    
    comment.delete(synchronize_session = False)
    db.commit()