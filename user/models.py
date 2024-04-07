from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime,Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# class Role(Base):
#     __tablename__='roles'
#     id = Column(Integer,primary_key=True,index=True)
#     name = Column(String)
#     user = relationship("User",back_populates="role")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    zipcode = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    # role_id = Column(Integer, ForeignKey("roles.id"))
    # role = relationship("Role",back_populates="user")
# Role.user = relationship("User",back_populates="role")

#forgot table
class PasswordResetRequest(Base):
    __tablename__ = "password_reset_requests"
    id = Column(Integer, primary_key=True, index=True)

    # email = Column(String, primary_key=True)
    email = Column(String)
    otp = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# class YelpReview(Base):
#     __tablename__ = "yelp_reviews"
#     id = Column(Integer, primary_key=True, index=True)
#     restaurant_name = Column(String)  
#     location = Column(String)
#     name = Column(String)
#     rating_id = Column(String)
#     rating = Column(Float)
#     text = Column(String)
#     submission_time = Column(DateTime)
#     created_at= Column(DateTime, default=datetime.utcnow)

