from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#changed secret key from fastapi doc
SECRET_KEY = f"{settings.secret_key}"
ALGORITHM = f"{settings.algorithm}"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes 

def create_jwt(data : dict):
    
    to_encode = data.copy()
    
    expiration_time = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expiration_time})
    
    encoded_token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    
    return encoded_token

def verify_token(token : str, credentials_exception):
    
    try:    #try except used becasue: if you inut wrong token : wihtout try,exc throws JWT Error;jose.exceptions.JWTError: Signature verification failed. so to handle we use try except
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        id:str = payload.get("user_id")
        
        if id is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=id) 
    
    except JWTError: 
        raise credentials_exception 
    
    # print(token_data) :=>output = "id = 15"
    return token_data

def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_token(token,credentials_exception)
    
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    
    return user
    
    