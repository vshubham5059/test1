from typing import List, Optional
from pydantic import BaseModel

class Role(BaseModel):
    name:str

class User(BaseModel):
    name:str
    email:str
    role_id:Optional[int] = None 

    class Config():

        from_attributes = True

class UserCreateSchema(User):
    password:str  
    zipcode:int
    # role_id:Optional[int] = None 
    class Config():
        from_attributes = True
class login(BaseModel):
    name:str
    password:str
    class Config():
        from_attributes = True

class log (BaseModel):
    name:str
    class Config():
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email:Optional[str] = None 
    class Config():
        from_attributes = True 

class ForgotPasswordRequest(BaseModel):
    email:str
    class Config():
        from_attributes = True 

class fetchdata(BaseModel):
    name:str
    location:str 
    class Config():
        from_attributes = True 
           
         