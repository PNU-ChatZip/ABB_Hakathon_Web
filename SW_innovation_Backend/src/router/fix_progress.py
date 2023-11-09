from fastapi import APIRouter, HTTPException,Query
from src.database.mongo import MongoHandler

router = APIRouter()
mongo_handler = MongoHandler()

@router.get('/update-location-progress')
async def update_location_progress(id:str, type:str, progress:str):
    print(id, type, progress)
    try:
        print("update_location_progress")
        mongo_handler.update_progress(type, id, progress)
        return {"message": "Location progress updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))