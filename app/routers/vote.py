from fastapi import FastAPI,Response,status, HTTPException, Depends, APIRouter 
from .. import database,schemas,models,oauth2
from sqlalchemy.orm import Session 


router = APIRouter(prefix="/vote",tags=['VOTE']) 

@router.post("/",status_code=status.HTTP_201_CREATED)
def post_vote(vote : schemas.Vote, current_user:models.User = Depends(oauth2.get_current_user),db:Session = Depends(database.get_db) ):
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No post with id {vote.post_id}")
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    
    if vote.dir:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"user already voted on {vote.post_id}") 
        else:
            new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
            db.add(new_vote)
            db.commit()
            return {"message":"vote successfully created"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user has not voted on {vote.post_id}")
        else:
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message":"vote removed"}
        