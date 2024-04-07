from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import user,reviews
from user import models,main
from reviews import models,main


user.models.Base.metadata.create_all(bind=engine)
reviews.models.Base.metadata.create_all(bind=engine)


app = FastAPI()
#user
app.include_router(user.main.router)
#reviews
app.include_router(reviews.main.router)

#reviews
# app.include_router(review.main.router)


# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# #registor_user
# @app.post("/user",tags=["user"],status_code=200,response_model=schemas.User)  
# def create_user(request:schemas.UserCreateSchema,db: Session = Depends(get_db)):
#     new_user=models.User(name=request.name,email=request.email,password=hashing.Hash.bcrypt(request.password),zipcode=request.zipcode,role_id=request.role_id)
#     existing_email = db.query(models.User).filter(models.User.email == request.email).first()
#     if existing_email:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

# # #seeall_user
# # @app.get("/users/",tags=["user"], response_model=List[schemas.User])
# # def all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
# #     user_all = db.query(models.User).offset(skip).limit(limit).all()
# #     return user_all

#  #seeall_user
# @app.get("/users/",tags=["user"], response_model=List[schemas.User])
# def all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user:schemas.User=Depends(oauth2.get_current_user)):
#     user_all = db.query(models.User).offset(skip).limit(limit).all()
#     return user_all

# #seeOne_user
# @app.get("/users/{id}",tags=["user"], response_model=schemas.User)
# def one_user(id=int,db: Session = Depends(get_db)):
#     single_user =db.query(models.User).filter(models.User.id == id).first()
#     if not single_user:
#         raise HTTPException(status_code=404,detail=f"not found")
#     return single_user


# #login_user
# app.include_router(authetication.router)

# #forgot
# app.include_router(forgot.router)

# #reviews_data
# app.include_router(reviews.router)
