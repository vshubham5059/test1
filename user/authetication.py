from typing import List
import psycopg2
from fastapi import Depends, FastAPI, HTTPException,APIRouter
from sqlalchemy.orm import Session
from . import  models,schemas,hashing,jwttoken
from fastapi.security import OAuth2PasswordRequestForm
from database import SessionLocal, engine
from passlib.context import CryptContext


router=APIRouter()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login",tags=["authetication"])
# def login(request:schemas.login,db: Session = Depends(get_db)):
def login(request:OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Username not found")
    
    if not hashing.Hash.verify(user.password,request.password):
        raise HTTPException(status_code=404, detail=f"wrong password")
    
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwttoken.create_access_token(data={"sub": user.email})
        # data={"sub": user.username}, expires_delta=access_token_expires
    
    return {"access_token": access_token, "token_type": "bearer"}

