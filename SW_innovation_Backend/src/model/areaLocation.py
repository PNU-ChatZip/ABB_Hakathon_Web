from pydantic import BaseModel, Field


class areaLocation(BaseModel):
    latitude: str
    longitude: str
    type:str
    time:str
    area1:str
    area2:str
    area3:str
    road:str
    progress:str
