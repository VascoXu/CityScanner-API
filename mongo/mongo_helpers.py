from pymongo import MongoClient
import time

def mongo_between_dates(collection, start, end, discard_fields=None):
    """Query MongoDB for documents between dates"""

    cursor = collection.find({
        "$expr": {
            "$and": [
                {
                    "$gte": [
                        "$time",
                        start
                    ]
                },
                {
                    "$lte": [
                        "$time",
                        end
                    ]
                },
            ]
        }
    }, discard_fields)
    
    return cursor