import re
from typing import Any, List
import uuid
from pydantic import BaseModel, Field, EmailStr, validator
from bson.objectid import ObjectId

class UserBaseModel(BaseModel):
    id: str | None = None
    fname: str = Field(max_length=100)
    lname: str = Field(max_length=100)
    email: EmailStr

class RequestModel(UserBaseModel):
    password: str

    @validator('password')
    def validate_password(cls, password):
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least 1 number")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least 1 lowercase letter")
        if not any(char in "!@#$%^&*()_+-=[]{};:,./<>?" for char in password):
            raise ValueError("Password must contain exactly 1 special character")
           
        return password

   # if not re.search(r'^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*()_+])\S{8,50}$', v):
            #     raise ValueError('Password must contain at least 1 number, 1 uppercase, 1 lowercase, and 1 special character.')  
    # password = user.password
    # if not any(char.isdigit() for char in password):
    #     raise HTTPException(status_code=400, detail="Password must contain at least 1 number")
    # if not any(char.isupper() for char in password):
    #     raise HTTPException(status_code=400, detail="Password must contain at least 1 uppercase letter")
    # if not any(char.islower() for char in password):
    #     raise HTTPException(status_code=400, detail="Password must contain at least 1 lowercase letter")
    # if not any(char in "!@#$%^&*()_+-=[]{};:,./<>?" for char in password):
    #     raise HTTPException(status_code=400, detail="Password must contain exactly 1 special character")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        # schema_extra = {
        #     "example": 
        #     {'_id': ObjectId('64196d6fab8106ed9f5769ff'), 'fname': 'sope', 'lname': 'adebayo', 'email': 'sopade@gmail.com', 'password': '1234'}
        # }

class ResponseModel(BaseModel):
    status: str
    user: UserBaseModel

class ListResponseModel(BaseModel):
    status: str
    users: List[UserBaseModel]
    pagination_data: Any
