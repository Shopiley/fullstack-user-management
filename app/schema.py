import re
from typing import Any, List
import uuid
from pydantic import BaseModel, Field, EmailStr, constr, validator
from bson.objectid import ObjectId

class UserBaseModel(BaseModel):
    id: str | None = None
    fname: str = Field(max_length=100)
    lname: str = Field(max_length=100)
    email: EmailStr

class RequestModel(UserBaseModel):
    password: constr(min_length=8, max_length=50)

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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ResponseModel(BaseModel):
    status: str
    user: UserBaseModel

class ListResponseModel(BaseModel):
    status: str
    users: List[UserBaseModel]
    pagination_data: Any

class UpdatePasswordModel(BaseModel):
    old_password: str
    new_password: constr(min_length=8, max_length=50)

    @validator('new_password')
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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    