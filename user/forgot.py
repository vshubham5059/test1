from typing import List
import psycopg2
from fastapi import Depends, FastAPI, HTTPException,APIRouter
from sqlalchemy.orm import Session
from . import  models,schemas,hashing,jwttoken
from fastapi.security import OAuth2PasswordRequestForm
from database import SessionLocal, engine
from passlib.context import CryptContext
from typing import Dict
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from sqlalchemy import desc




router=APIRouter()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# @router.post("/forgot-password/")
# def forgot_password(request: schemas.ForgotPasswordRequest,db: Session = Depends(get_db)):
#     if request.email:
#         otp = generate_otp()  
#         # Store OTP in the database
#         password_reset_request = models.PasswordResetRequest(email=request.email, otp=otp)
#         db.add(password_reset_request)
#         db.commit()

#         # Send OTP via email
#         send_otp_email(request.email, otp)
#         return {"message": "OTP sent successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Email is required")



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
@router.post("/reset-passwordd/",tags=["forgot-password"])
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

