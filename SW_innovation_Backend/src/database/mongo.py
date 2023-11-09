from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoHandler:
    def __init__(self, uri='mongodb://chatzip:mongo^^chatzip@mongo:27017', db_name='location_db'):
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            self.forthole = self.db['forthole']
            self.accident = self.db['accident']
            self.traffic_jam = self.db['traffic_jam']
            self.counters = self.db['counters']
            print("MongoDB connected successfully.")
        except ConnectionFailure as cf:
            print(f"Connection to MongoDB failed: {cf}")
            raise
    
    def get_next_sequence(self, name):
        # 카운터 컬렉션에서 시퀀스를 가져오고 증가시킴
        sequence_document = self.counters.find_one_and_update(
            {'_id': name},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=True
        )
        return sequence_document['seq'] if sequence_document else 1

    def insert_location(self, location_data):
        next_id = self.get_next_sequence(location_data["type"])
        location_data['id'] = next_id
        
        if location_data["type"] == "포트홀":
            self.forthole.insert_one(location_data)
            print(f"forthole Location inserted: {location_data}")
        
        if location_data["type"] == "차량 사고":
            self.accident.insert_one(location_data)
            print(f"accident Location inserted: {location_data}")
        
        if location_data["type"] == "도로 막힘":
            self.traffic_jam.insert_one(location_data)
            print(f"traffic_jam Location inserted: {location_data}")

    def get_forthole_locations(self):
        locations = list(self.forthole.find({}, {'_id': 0}))
        return locations
    
    def get_accident_locations(self):
        locations = list(self.accident.find({}, {'_id': 0}))
        return locations
    
    def get_traffic_jam_locations(self):
        locations = list(self.traffic_jam.find({}, {'_id': 0}))
        return locations
    
    def delete_forthole_locations(self):
        self.forthole.delete_many({})
        print("All forthole locations deleted.")
    
    def delete_accident_locations(self):
        self.accident.delete_many({})
        print("All accident locations deleted.")
        
    def delete_traffic_jam_locations(self):
        self.traffic_jam.delete_many({})
        print("All traffic_jam locations deleted.")
        
    
    def update_progress(self, doc_type, doc_id, progress):
    # 컬렉션을 type에 따라 선택
        collection = None
        
        if doc_type == "forthole":
            collection = self.forthole
        elif doc_type == "accident":
            collection = self.accident
        elif doc_type == "traffic_jam":
            collection = self.traffic_jam
        
        if collection is not None:
            print(f"Updating {doc_type} document with id {doc_id} with progress: {progress}")
            result = collection.update_one(
                {'id': int(doc_id)},
                {'$set': {'progress': progress}}
            )
            if result.matched_count > 0:
                print(f"{doc_type} document with id {doc_id} has been updated with progress: {progress}")
                return True
            else:
                print(f"No {doc_type} document found with id {doc_id}.")
                return False
        else:
            print(f"Invalid document type: {doc_type}. Please choose from '포트홀', '차량 사고', '도로 막힘'.")
            return False


    
    
