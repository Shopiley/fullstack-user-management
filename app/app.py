from pathlib import Path
from fastapi import FastAPI, APIRouter, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from pymongo import MongoClient, ReturnDocument
from schema import RequestModel, ResponseModel, ListResponseModel, UpdatePasswordModel
from typing import List
from serializer import userEntity, userListEntity
from bson.objectid import ObjectId
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from database import collection
from passlib.context import CryptContext

app = FastAPI()
print("app initialized! ")
origins = ["http://127.0.0.1:8888", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    print(verify_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    print(get_password_hash)
    return pwd_context.hash(password)
# -------------------------------------------------------------------------------
# This is supposed to render the new-html page on this URl - http://127.0.0.1:8000/ 
# so that this html page is displayed once you run the app but it's not working. 
# I haven't been able to figure out the problem so far. And I couldn't continue as the time limit on this test had elapsed

template_dir = "templates"

# Create a Jinja2 environment
env = Environment(loader=FileSystemLoader(template_dir))

# Define your route
@app.get("/")
async def index(request: Request):
    # Return the rendered HTML template as a response
    return HTMLResponse(content=env.get_template("home.html").render(), status_code=200)

@app.get("/new-user")
async def index(request: Request):
    return HTMLResponse(content=env.get_template("new-user.html").render(), status_code=200)

@app.get("/view-users")
async def index(request: Request):
    return HTMLResponse(content=env.get_template("view-users.html").render(), status_code=200)

@app.get("/edit-password")
async def index(request: Request):
    return HTMLResponse(content=env.get_template("edit-password.html").render(), status_code=200)
# -------------------------------------------------------------------------------


@router.post('/', response_description="Creates a new user", status_code=status.HTTP_201_CREATED, response_model = ResponseModel)
def create_user(payload: RequestModel):
    try:
        payload.password = get_password_hash(payload.password)
        print(payload)
        new_user = collection.insert_one(payload.dict())
        response = collection.find_one({'_id': new_user.inserted_id}, {"password":0})
        return {"status": "success", "user": userEntity(response)}
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,  detail={"status": "error", "message": f"User with email: {payload.email} already exists"})


@router.get("/", response_description="Lists all users", response_model= ListResponseModel)
async def get_users(limit: int = 10, page: int = 1, search: str = ''):   
    skip = (page - 1) * limit
    query = {'$or': [{'fname': {'$regex': search, '$options': 'i'}},
                    {'email': {'$regex': search, '$options': 'i'}}]}
    total_count = collection.count_documents(query)
    cursor = collection.find(query).limit(limit).skip(skip)
    users = userListEntity(cursor)
    pagination_data = {"page": page, "limit": limit, "total_count": total_count}
    return {"status": "success", "users": users, "pagination_data": pagination_data}


@router.get('/{userId}', response_model=ResponseModel)
def get_user(userId: str):
    print(userId)
    user = collection.find_one({'_id': ObjectId(userId)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No user with this userId: {userId} found")
    return {"status": "success", "user": userEntity(user)}


@router.patch('/{userId}', response_model=ResponseModel)
def update_password(userId: str, payload:UpdatePasswordModel):
    print(userId, "from patch")
    user = collection.find_one({'_id': ObjectId(userId)})
    print(user)
    if verify_password(payload.old_password, user["password"]) == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"old password entered is not correct for user with userId: {userId}")
    
    updated_user = collection.find_one_and_update(
        {"_id": userId}, 
        {'$set': {"password": get_password_hash(payload.new_password)}},
        return_document=ReturnDocument.AFTER
    )
    print(updated_user)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user with this user id: {userId} found")
    
    return {"status": "success", "user": userEntity(updated_user)}

app.include_router(
    router, prefix='/api/users', tags=["Users"]
)

