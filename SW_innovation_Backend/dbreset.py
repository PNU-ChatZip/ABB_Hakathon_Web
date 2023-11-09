from src.database.mongo import MongoHandler

mongo = MongoHandler()

mongo.delete_forthole_locations()
mongo.delete_accident_locations()
mongo.delete_traffic_jam_locations()