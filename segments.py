import io
import os

import numpy as np
import pandas as pd
import osmnx as ox
from geojson import FeatureCollection, Feature, Point, dumps, dump
from mapbox import Uploader
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint
from sklearn.neighbors import BallTree

from datetime import datetime

from mongo.mongo import *

# configure MongoDB
MONGO_URL = os.environ.get("MONGO_URL")
MONGO_DB = os.environ.get("MONGO_DB")
mongodb = MongoConnection(url=MONGO_URL, db=MONGO_DB)

"""
# query MongoDB
collection = "NYC_2_MOB_DATA"
# rows = mongodb.find(collection=collection, limit=10)
# data = pd.DataFrame(rows)
data = pd.read_csv("AQ.csv")
data = data[["temp_ext", "hum_ext", "pm25", "pm10", "long", "lat", "time"]]
data = data.dropna()
# data = data[:10]
"""

"""
# configure mapbox
mapbox_token = "sk.eyJ1IjoidmFzY294dSIsImEiOiJja28yM2NteWswMzNrMm5vN2loZHpxcXVoIn0.HPJt_e8pbYkU3wM02Z_fcg"
bbox = [40.9457, 40.4774, -73.7002, -74.2591]
# G = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')
"""

#  data = pd.read_csv("AQ.csv")
#     data = data[["temp_ext", "hum_ext", "pm25", "pm10", "long", "lat", "time"]]
#     data = data.dropna()
#     data = data[1:10]

def create_segments(data, bbox):
    """
    Matches data from DataFrames to the driving streets OpenStreetMap network area specified by bbox.
    :param pd.DataFrame data: A dataframe with the data points to attach to segments. Must have "lat" and "long" columns
    :param list bbox: A geographic bounding box of north, south, east, and west values, respectively
    """

    nb, sb, eb, wb = bbox
    G = ox.graph_from_bbox(nb, sb, eb, wb)
    dist = 0.0001
    edges = ox.utils_graph.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
    edges['index'] = range(1, len(edges)+1)

    # Get closest point on each segment
    lng = data['long']
    lat = data['lat']
    ne, dist = ox.distance.nearest_edges(G, lng, lat, return_dist=True)

    # Format edges to upload to mapbox
    all_edges = []
    all_lines = []
    for n in ne:
        u, v, key = n
        edge = edges.loc[(u, v, key), "geometry"]
        index = edges.loc[(u, v, key), "index"]
        if edge not in all_edges:
            feature = Feature(id=int(index), geometry=edge)
            all_edges.append(edge)
            all_lines.append(feature)
    all_lines = FeatureCollection(all_lines)

    return all_lines


def upload_to_mapbox(geojson_object, tileset_name, mapbox_token):
    """
    Uploads a GeoJSON object to Mapbox as a tileset.
    :param geojson_object: A GeoJSON compatible object to encode
    :param str tileset_name: The tileset name in Mapbox
    :return: An object containing the response from Mapbox
    """

    # Upload to mapbox
    uploader = Uploader(access_token=mapbox_token)
    geojson_file = io.BytesIO(dumps(geojson_object).encode())
    upload_resp = uploader.upload(geojson_file, tileset_name)
    geojson_file.close()
    return upload_resp.json()


def averages(data, bbox):
    """
    Matches data from DataFrames to the driving streets OpenStreetMap network area specified by bbox.
    :param pd.DataFrame data: A dataframe with the data points to attach to segments. Must have "lat" and "long" columns
    :param list bbox: A geographic bounding box of north, south, east, and west values, respectively
    """

    # load mapbox
    nb, sb, eb, wb = bbox
    G = ox.graph_from_bbox(nb, sb, eb, wb)
    dist = 0.0001
    edges = ox.utils_graph.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
    edges['index'] = range(1, len(edges)+1)

    all_data = dict()
    for index, row in data.iterrows():
        date = datetime.fromtimestamp(row['time'])
        print(date)
        if date not in all_data:
            all_data[date] = [row]
        else:
            all_data[date].append(row)

    rows = []
    for key, value in all_data.items():
        # get closest point on each segment
        lng = value['long']
        lat = data['lat']
        ne, dist = ox.distance.nearest_edges(G, lng, lat, return_dist=True)
        print(ne)
        
    rows.append({""})

averages()


         
    