# from typing import Union, List
from fastapi import FastAPI, APIRouter, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from schema import RequestModel, ResponseModel, ListResponseModel
from typing import List
from serializer import userEntity, userListEntity
from bson.objectid import ObjectId

app = FastAPI()
router = APIRouter()


# , server_api=ServerApi('1')
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

    # return JSONResponse(
    #     content=ResponseModel.success(data=response.dict(), message="user created"),
    #     status_code=status.HTTP_201_CREATED,
    # )


@router.get("/users", response_description="Lists all users", response_model= ListResponseModel)
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
    if not ObjectId.is_valid(userId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {userId}")

    user = collection.find_one({'_id': ObjectId(userId)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No user with this id: {userId} found")
    return {"status": "success", "user": userEntity(user)}


app.include_router(
    router, prefix='/api/users', tags=["Users"]
)