from .. import models, schemas, utils
from sqlalchemy.orm import Session
from fastapi import FastAPI,Response,status, HTTPException, Depends, APIRouter
from ..database import get_db 

router = APIRouter(
    prefix='/user',
    tags=['Users']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(uinfo:schemas.User,db : Session = Depends(get_db)) -> schemas.UserResponse:
    emails = db.query(models.User.email).all()
    if (uinfo.email,) in emails:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail = f"{uinfo.email} already exists")
    uinfo.password = utils.hasher(uinfo.password)
    user_info = models.User(**uinfo.model_dump())
    db.add(user_info)
    db.commit()
    db.refresh(user_info)
    return user_info

@router.get('/{id}')
def get_user(id:int , db:Session = Depends(get_db)) -> schemas.UserResponse:
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"uid {id} does not exist")
    
    return user