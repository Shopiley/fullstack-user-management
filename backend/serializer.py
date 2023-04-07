from bson.objectid import ObjectId

def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "fname": user["fname"],
        "lname": user["lname"],
        "email": user["email"],
    }

def userListEntity(users) -> list:
    return [userEntity(user) for user in users]