from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

client = MongoClient(config["DATABASE_URI"])
db = client[config["DATABASE_NAME"]]
print("Connected to the MongoDB server!🚀")
collection = db.users
collection.create_index("email", unique=True)
