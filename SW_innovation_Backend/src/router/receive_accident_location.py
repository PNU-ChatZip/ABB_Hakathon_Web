from fastapi import APIRouter
from src.database.mongo import MongoHandler

router = APIRouter()
mongo_handler = MongoHandler()

@router.get("/receive-accident-location")
async def receive_location():
    locations = mongo_handler.get_accident_locations()
    return locations
