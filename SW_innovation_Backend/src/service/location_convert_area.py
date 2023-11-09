from src.model.Location import Location
from src.model.areaLocation import areaLocation
from src.service.get_area import get_area
from src.service.get_geocoding_reverse import geocoding_reverse

def location_convert_area(location:Location):
    location_dict = location.dict()
    print(location_dict)
    # Call get_area with latitude and longitude
    area = get_area(location_dict["longitude"]+","+location_dict["latitude"])
    road = geocoding_reverse(location_dict["latitude"]+","+location_dict["longitude"])
    
    # Now area should contain the area information, make sure it's in the correct format
    # Let's assume area is a dictionary that has 'area1', 'area2', and 'area3' keys
    # If the structure is different, you need to modify the code accordingly
    area = area["results"][0]['region']
    # Create areaLocation instance
    location_info = areaLocation(
        latitude=location_dict["latitude"],
        longitude=location_dict["longitude"],
        type=location_dict["type"],
        time=location_dict["time"],
        area1=area["area1"]["name"],
        area2=area["area2"]["name"],
        area3=area["area3"]["name"],
        road=road,
        progress="discovered"
    )
    
    return location_info.dict()