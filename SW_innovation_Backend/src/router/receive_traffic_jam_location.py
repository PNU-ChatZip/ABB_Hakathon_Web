from fastapi import APIRouter
from src.database.mongo import MongoHandler

router = APIRouter()
mongo_handler = MongoHandler()

@router.get("/receive-traffic-jam-location")
async def receive_location():
    locations = mongo_handler.get_traffic_jam_locations()
    return locations
