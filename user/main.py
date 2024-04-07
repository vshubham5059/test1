from database import SessionLocal, engine
from typing import List
import psycopg2
from fastapi import Depends, FastAPI, HTTPException,APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import  jwttoken
from . import  models, schemas,hashing,authetication,oauth2,forgot
from passlib.context import CryptContext
from typing import Dict
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from sqlalchemy import desc

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#registor_user
@router.post("/register-user",tags=["user"],status_code=200,response_model=schemas.User)  
def create_user(request:schemas.UserCreateSchema,db: Session = Depends(get_db)):
    new_user=models.User(name=request.name,email=request.email,password=hashing.Hash.bcrypt(request.password),zipcode=request.zipcode)
    existing_email = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# #seeall_user
# @app.get("/users/",tags=["user"], response_model=List[schemas.User])
# def all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     user_all = db.query(models.User).offset(skip).limit(limit).all()
#     return user_all

 #seeall_user
@router.get("/users/",tags=["user"], response_model=List[schemas.User])
def all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user:schemas.User=Depends(oauth2.get_current_user)):
    user_all = db.query(models.User).offset(skip).limit(limit).all()
    return user_all

#seeOne_user
@router.get("/users/{id}",tags=["user"], response_model=schemas.User)
def one_user(id=int,db: Session = Depends(get_db)):
    single_user =db.query(models.User).filter(models.User.id == id).first()
    if not single_user:
        raise HTTPException(status_code=404,detail=f"not found")
    return single_user



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


#forgot
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via email
def send_otp_email(email: str, otp: str):
    # Sender email details
    sender_email = "vshubham5059@gmail.com"  
    sender_password = "Vshubham@5059"  
    message = f"Your OTP for password reset is: {otp}"
    msg = MIMEText(message)
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = sender_email
    msg["To"] = email

    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Error sending email:", e)

@router.post("/forgot-password/",tags=["forgot-password"])
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    if request.email:
        # Check if there's an existing pending password reset request for the provided email
        existing_request = db.query(models.PasswordResetRequest).filter(
            models.PasswordResetRequest.email == request.email
        ).first()

        if existing_request:
            # Check if the existing OTP has expired or not
            current_time = datetime.utcnow()
            if current_time < existing_request.created_at + timedelta(minutes=5):  # Assuming OTP expires after 5 minutes
                raise HTTPException(status_code=400, detail="An active OTP exists for this email. Please wait for 5 minutes before requesting again.")
            else:
                # Expire the existing OTP
                existing_request.is_expired = True
                db.commit()

        # Generate new OTP and store it in the database
        otp = generate_otp()
        password_reset_request = models.PasswordResetRequest(email=request.email, otp=otp)
        db.add(password_reset_request)
        db.commit()

        # Send OTP via email
        send_otp_email(request.email, otp)
        return {"message": "OTP sent successfully"}
    else:
        raise HTTPException(status_code=400, detail="Email is required")

#reset-password
@router.post("/reset-password/",tags=["forgot-password"])
def reset_password(email: str, otp: str, new_password: str,db: Session = Depends(get_db)):
    reset_request = db.query(models.PasswordResetRequest).filter(models.PasswordResetRequest.email == email,models.PasswordResetRequest.otp == otp).first()
    if reset_request and reset_request.otp == otp:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            # Update user's password
            user.password = hashing.Hash.bcrypt(new_password)
            db.delete(reset_request)
            db.commit()
            return {"message": "Password reset successful"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP or email")


@router.post("/reset-passwordd/",tags=["forgot-password"])
def resetre_password(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):
    reset_request = db.query(models.PasswordResetRequest).filter(models.PasswordResetRequest.email == email).order_by(desc(models.PasswordResetRequest.created_at)).first()
    if reset_request and reset_request.otp == otp:
        # Check if the OTP is not expired (assuming there's a 'created_at' field in the PasswordResetRequest model)
        current_time = datetime.utcnow()
        if current_time - reset_request.created_at <= timedelta(minutes=5):  # Adjust the time window as needed
            user = db.query(models.User).filter(models.User.email == email).first()
            if user:
                # Update user's password
                user.password = hashing.Hash.bcrypt(new_password)
                db.delete(reset_request)
                db.commit()
                return {"message": "Password reset successful"}
            else:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=400, detail="OTP expired")
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP or email")


#reviews_data
# app.include_router(reviews.router)
