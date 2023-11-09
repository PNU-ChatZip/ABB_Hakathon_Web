import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_area(coords):
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    # 좌표 (경도, 위도)
    output = "json"
    orders = 'addr'
    endpoint = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"
    url = f"{endpoint}?coords={coords}&output={output}&orders={orders}"

    # 헤더
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }

    # 요청
    res = requests.get(url, headers=headers)
    return res.json()