import csv
from src.database.mongo import MongoHandler
from src.service.get_area import get_area
from src.service.get_geocoding_reverse import geocoding_reverse
from src.service.location_convert_area import location_convert_area
from src.model.Location import Location
from src.model.areaLocation import areaLocation
from datetime import datetime, timedelta
import random
import requests
from pydantic import ValidationError
from geopy.geocoders import Nominatim
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB 연결 설정
mongo_handler = MongoHandler()

# CSV 파일 경로
csv_file_path = os.getenv('CSV_FILE_PATH')

def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())))

# Start date (January 1st, 2022)
start_date = datetime(2022, 1, 1)

# End date (Current date)
end_date = datetime.now()

# Generate a random datetime between the start and end dates

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        try:
            random_datetime = random_date(start_date, end_date)
            formatted_datetime = random_datetime.strftime("%Y-%m-%d %H:%M:%S")
            # print(csv_reader.line_num, row)
            location_data = Location(
                latitude=row['위도'],  # Replace comma with dot if needed
                longitude=row['경도'],  # Replace comma with dot if needed
                type='차량 사고',  # 사고로 고정
                time=formatted_datetime
            )
            converted_location = location_convert_area(location_data)
            print(converted_location)
            mongo_handler.insert_location(converted_location)
        except ValidationError as ve:
            print(f"Data validation error: {ve}")
        except Exception as e:
            print(f"An error occurred: {e}")
    

# Fetch and print accident locations to confirm insertion
try:
    print(mongo_handler.get_accident_locations())
except Exception as e:
    print(f"An error occurred when fetching accident locations: {e}")

