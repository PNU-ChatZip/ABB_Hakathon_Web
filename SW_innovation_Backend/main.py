# main.py

from fastapi import FastAPI
import uvicorn
from src.router.send_location import router as send_location_router
from src.router.receive_accident_location import router as receive_accident_location_router
from src.router.receive_traffic_jam_location import router as receive_traffic_jam_location_router
from src.router.receive_forthole_location import router as receive_forthole_location_router
from src.router.fix_progress import router as fix_progress_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(send_location_router)
app.include_router(receive_accident_location_router)
app.include_router(receive_traffic_jam_location_router)
app.include_router(receive_forthole_location_router)
app.include_router(fix_progress_router)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=1101)
