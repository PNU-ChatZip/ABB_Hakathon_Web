from pydantic import BaseModel

class Location(BaseModel):
    latitude: str
    longitude: str
    type:str
    time:str