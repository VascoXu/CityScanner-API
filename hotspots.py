from mongo.mongo import *
import pytz
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import folium
import json
from folium import plugins

from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint

from sklearn.neighbors import BallTree

def isfloat(elem):
    try:
        float(elem)
    except:
        return False
    return True


def calculate_hotspots(data):
    """Calculate hotspots given a Pandas dataframe"""

    # Drop all rows with lat or long = 0
    data = data.loc[(data[['lat', 'long', 'pm25']] != 0).all(axis=1)]
    data = data[data['lat'].apply(lambda x: isfloat(x))]
    data = data[data['long'].apply(lambda x: isfloat(x))]
    print(data)
    print(data['long'].apply(lambda x: isfloat(x)))

    # Grab only pm2.5 values >100 like the R code 
    latavg = data['lat'].mean()
    longavg = data['long'].mean()
    #and grab only pm2.5 values >100 like the R code 
    data = data.loc[(data['pm25'] > 100)]
    data = data.loc[(data['lat'] > (latavg-5))]
    data = data.loc[(data['long'] > (longavg-5))]
    data = data.loc[(data['lat'] < (latavg+5))]
    data = data.loc[(data['long'] < (longavg+5))]

    # Use the locations of the hotspot clusters to determine where the map displays
    def get_centermost_point(cluster):
        centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
        centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
        return tuple(centermost_point)

    coords = data.loc[:,['lat','long']].values
    start_point=coords[0]

    # Setting up the specifications for the map
    foliumMap = folium.Map(location= start_point, tiles='Stamen Terrain', zoom_start=14)
    # Creating the hotspots on the map
    for i,row in data.iterrows():
        folium.CircleMarker((row.lat,row.long), radius=10, weight=2, color='red', fill_color='red', fill_opacity=.5).add_to(foliumMap)

    # Saving an html version of the map users can zoom in and out of and interact with
    foliumMap.save('foliumPointMap.html')

    # Setting up the specifications for the map
    foliumMap = folium.Map(location=start_point, tiles='Stamen Terrain', zoom_start=14)

    # Creating the hotspots on the map
    for i,row in data.iterrows():
        folium.CircleMarker((row.lat,row.long), radius=10, weight=2, color='red', fill_color='red', fill_opacity=.5).add_to(foliumMap)

    # Adding heatmap functionality
    foliumMap.add_child(plugins.HeatMap(data[['lat', 'long']].to_numpy(), radius=25))

    # Saving an html version of the map users can zoom in and out of and interact with
    foliumMap.save('foliumHeatmap.html')

    hotspots = data 
    coords = hotspots.loc[:,['lat','long']].values.astype(int)

    # Preprocessing for hotspot clustering
    kms_per_radian = 6371.0088
    epsilon = 0.1 / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=10, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))-(1 if -1 in set(cluster_labels) else 0)
    outliers = coords[cluster_labels == -1]

    # Creating the clusers
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    outliers = coords[cluster_labels == -1]
    centermost_points = clusters.map(get_centermost_point)
    start_point=centermost_points[0]
    print('Number of clusters: {}'.format(num_clusters))

    centermost_points = clusters.map(get_centermost_point)
    start_point=centermost_points[0]

    # Setting up the specifications for the map
    newmap = folium.Map(location= start_point, tiles='Stamen Toner', zoom_start=14)
    points=[]
    # Add markers
    for index, row in hotspots.iterrows():
        point=(row['lat'], row['long'])
        if point not in points:
            new_point=(row['lat'], row['long'])
            points.append(new_point)      
    for rep in centermost_points:
        folium.CircleMarker(location=rep, color='blue', fill=True, fill_color='blue',radius=20).add_to(newmap)
    for each in points:
        folium.CircleMarker(location=each, popup='Point:'+str(each), color='red', fill=True, fill_color='red',radius=10).add_to(newmap)
        newmap.add_child(folium.LatLngPopup())

    # Interactive html map showing hotspot clusters
    newmap.save('templates/foliumHotspotMap.html')