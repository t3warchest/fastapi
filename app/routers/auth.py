from fastapi import FastAPI,Response,status, HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
from .. import database,schemas,models,utils,oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model=schemas.AccessToken)
def login(user_credentials:schemas.UserLogin, db:Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    # if not utils.hasher(user_credentials.password) == user.password: does not work
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth2.create_jwt({"user_id":user.id })
    
    return {"access_token":access_token, "token_type" :"bearer"}