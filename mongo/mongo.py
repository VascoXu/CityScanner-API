import time
from datetime import datetime

from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps, default

from helpers import string_to_datetime
from mongo.mongo_helpers import *

class MongoConnection:
    def __init__(self, url, db, collection=None):
        """Constructor for initializing a MongoDB connection"""

        client = MongoClient(url)
        self.db = client[db]
        self.collection = db[collection] if (collection) else None
        
    def find(self, collection, timezone=None, limit=None, start=None, end=None):
        """Find documents from MongoDB"""

        discard_fields = { "_id": 0}
        self.collection = self.db[collection]
        if start and end:
            start = int(string_to_datetime(start, timezone).timestamp())
            end = int(string_to_datetime(end, timezone).timestamp())
            cursor = mongo_between_dates(self.collection, start, end, discard_fields=discard_fields)
        else:
            cursor = self.collection.find({}, discard_fields)

        if limit:
            cursor = cursor.limit(int(limit))

        # TODO: Handle LARGE datasets (pagination)
        return cursor


    def get_start_date(self, collection):
        """Find first valid date of collection"""

        start = self.db[collection].find({
            "time": {
                "$gt": 1514782800 # 2018
            }
        }).sort("time", ASCENDING).limit(1) # find start date
        return start


    def get_end_date(self, collection):
        """Find last valid date of collection"""

        end = self.db[collection].find({
            "time": {
                "$lt": int(time.time()) # current unix time
            }
        }).sort("time", DESCENDING).limit(1) # find end date
        return end


    def list_collections(self):
        """List all available collections"""
        
        collections = self.db.list_collection_names()
        return collections

    
    def summary(self):
        """Summary of MongoDB collections"""

        # Query all available collections
        collections = self.db.list_collection_names()

        summary = []
        for collection in collections:
            # Ignore collections
            col_name = collection.lower()
            if "_war" in col_name or "warnings" in col_name:
                continue
            
            count = self.db[collection].count_documents({}) # find number of datapoints
            # devices = len(self.db[collection].distinct('deviceID')) # find number of devices
            start = self.get_start_date(collection) # find start date
            end = self.get_end_date(collection) # find end date

            # Package data into a dict
            try:
                summary.append({
                    'dataset': collection,
                    'start': list(start)[0]['time'],
                    'end': list(end)[0]['time'], 
                    'count': count
                })            
            except:
                pass

        return summary