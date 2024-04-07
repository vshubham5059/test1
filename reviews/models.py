from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime,Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# class Role(Base):
#     __tablename__='roles'
#     id = Column(Integer,primary_key=True,index=True)
#     name = Column(String)
#     user = relationship("User",back_populates="role")


# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     email = Column(String)
#     password = Column(String)
#     is_active = Column(Boolean, default=True)
#     zipcode = Column(Integer)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#     role_id = Column(Integer,ForeignKey("roles.id"))
#     role = relationship("Role",back_populates="user")
# # Role.user = relationship("User",back_populates="role")

# #forgot table
# class PasswordResetRequest(Base):
#     __tablename__ = "password_reset_requests"
#     id = Column(Integer, primary_key=True, index=True)

#     # email = Column(String, primary_key=True)
#     email = Column(String)
#     otp = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)

class YelpReview(Base):
    __tablename__ = "yelp_reviews"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String)  
    location = Column(String)
    review_id= Column(String)
    name = Column(String)
    rating = Column(Float)
    text = Column(String)
    submission_time = Column(DateTime)
    created_at= Column(DateTime, default=datetime.utcnow)

class YelpScrapReview(Base):
    __tablename__ = "yelp_scrap_reviews"
    id = Column(Integer, primary_key=True, index=True)
    source=Column(String)
    restaurant_name = Column(String)  
    location = Column(String)
    review_id= Column(String)
    name = Column(String)
    rating = Column(Float)
    text = Column(String)
    submission_time = Column(DateTime)
    created_at= Column(DateTime, default=datetime.utcnow)

class Restaurant(Base):
    __tablename__="restaurant"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String) 
    restaurant_score = Column(Float) 
    res = relationship("Review",back_populates="rev")


class Review(Base):
    __tablename__="review"
    id = Column(Integer, primary_key=True, index=True)
    review_type=Column(String)
    common_id=Column(Integer,ForeignKey("restaurant.id"))
    review=Column(String)
    intent=Column(String)
    food=Column(list)
    drink=Column(list)
    review_sentiment=Column(String)
    food_sentiment=Column(String)
    staff=Column(String)
    drink_sentiment=Column(String)
    service_sentiment=Column(String)
    delivery_sentiment=Column(String)
    sentiment_score=Column(Integer)
    rev=relationship("Restaurant",back_populates="res")






