from fastapi import APIRouter
from src.database.mongo import MongoHandler
from src.model.Location import Location
from src.model.areaLocation import areaLocation
from src.service.location_convert_area import location_convert_area
import requests
import json
from geopy.geocoders import Nominatim
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
mongo_handler = MongoHandler()

@router.post("/send-location")
async def send_location(location:Location):
    convertedLocation = location_convert_area(location)
    print(convertedLocation)
    mongo_handler.insert_location(convertedLocation)
    print(convertedLocation)

    return {"message": "Location received successfully"}