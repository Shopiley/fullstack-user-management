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
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# -------------------------------------------------------------------------------
# This is supposed to render the new-html page on this URl - http://127.0.0.1:8000/ 
# so that this html page is displayed once you run the app but it's not working. 
# I haven't been able to figure out the problem so far. And I couldn't continue as the time limit on this test had elapsed
BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'frontend')))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("new-user.html", {"request": request})
# -------------------------------------------------------------------------------

client = MongoClient('mongodb+srv://adebayomoshope:shopsy2004@cluster0.fpt2kf3.mongodb.net/?retryWrites=true&w=majority&connectTimeoutMS=10000&socketTimeoutMS=10000')
db = client.moni_users
print("Connected to the MongoDB server")
collection = db.users
collection.create_index("email", unique=True)


@router.post('/', response_description="Creates a new user", status_code=status.HTTP_201_CREATED, response_model = ResponseModel)
def create_user(payload: RequestModel):
    try:
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


@router.get('/{email}', response_model=ResponseModel)
def get_user(email: EmailStr):
    user = collection.find_one({'email': email})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No user with this email: {email} found")
    return {"status": "success", "user": userEntity(user)}


@router.patch('/{email}', response_model=ResponseModel)
def update_user(email: EmailStr, payload:UpdatePasswordModel):
    user = collection.find_one({'email': email})
    
    if user["password"] != payload.old_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"old password entered is not correct for user with email: {email}")
    
    updated_user = collection.find_one_and_update(
        {"email": email}, 
        {'$set': {"password": payload.new_password}},
        return_document=ReturnDocument.AFTER
    )

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user with this email: {email} found")
    
    return {"status": "success", "user": userEntity(updated_user)}

app.include_router(
    router, prefix='/api/users', tags=["Users"]
)

# app.mount("/", StaticFiles(directory="moni-africa-backend-test\frontend.new-user"), name="index")