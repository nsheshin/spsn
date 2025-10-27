from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URL = "mongodb://root:secretpassword@mongo:27017/mydb?authSource=admin"
MONGO_DB = "files_db"
MONGO_COLLECTION = "uploaded_files"
QUESTIONS_COLLECTION = "questions"

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
files_collection  = db[MONGO_COLLECTION]
questions_collection = db[QUESTIONS_COLLECTION]
