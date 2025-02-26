import ee
import json
import os
import math
import requests
import numpy as np
import io
from PIL import Image
from io import BytesIO
import time
from staticmap import StaticMap

def mask_s2_clouds(image):
  qa = image.select('QA60')
  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloud_bit_mask = 1 << 10
  cirrus_bit_mask = 1 << 11
  # Both flags should be set to zero, indicating clear conditions.
  mask = (
      qa.bitwiseAnd(cloud_bit_mask)
      .eq(0)
      .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
  )
  return image.updateMask(mask)

def mask_viirs_nighttime(image):
    # Select the cloud-free coverage band
    cf_cvg = image.select('cf_cvg')
    # Set a threshold for the minimum number of observations
    # You may need to adjust this threshold based on your specific requirements
    min_observations = 3
    # Create a mask where cf_cvg is greater than or equal to the threshold
    mask = cf_cvg.gte(min_observations)
    # Apply the mask to the image
    return image.updateMask(mask)

def init_gee():
    service_account = 'my-service-account@...gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './private-key.json')
    ee.Initialize(credentials)

def s2_2021():
    # https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
    image_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    image_collection = image_collection.filterDate('2021-05-01', '2021-09-01')
    image_collection = image_collection.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 1))
    image_collection = image_collection.map(mask_s2_clouds)
    image = image_collection.mean()
    return image

def viirs_2021():
    # https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG
    image_collection = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
    image_collection = image_collection.filterDate('2021-01-01', '2022-01-01')
    image_collection = image_collection.map(mask_viirs_nighttime)
    image = image_collection.mean()
    return image

def s1_2021():
    # https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
    image_collection = ee.ImageCollection("COPERNICUS/S1_GRD") \
        .filterDate('2021-07-01', '2021-08-01') \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
        .filter(ee.Filter.eq('instrumentMode', 'IW'))  # Ensures Interferometric Wide swath mode
    image = image_collection.mean()
    return image

def census_1000_2021():
    table = 'projects/ginsed2019/assets/census_2021_1000'
    featureCollection = ee.FeatureCollection(table)
    image = featureCollection.reduceToImage(properties=['den'], reducer=ee.Reducer.first()).rename('den')
    return image

def census_500_2021():
    table = 'projects/ginsed2019/assets/census_2021_500'
    featureCollection = ee.FeatureCollection(table)
    image = featureCollection.reduceToImage(properties=['den'], reducer=ee.Reducer.first()).rename('den')
    return image

def census_250_2021():
    table = 'projects/ginsed2019/assets/census_2021_250'
    featureCollection = ee.FeatureCollection(table)
    image = featureCollection.reduceToImage(properties=['den'], reducer=ee.Reducer.first()).rename('den')
    return image

def census_100_2021():
    table = 'projects/ginsed2019/assets/census_2021_100'
    featureCollection = ee.FeatureCollection(table)
    image = featureCollection.reduceToImage(properties=['den'], reducer=ee.Reducer.first()).rename('den')
    return image

def census_2021():
    table = 'projects/ginsed2019/assets/pop_density_per_100_m_x_100_m'
    featureCollection = ee.FeatureCollection(table)
    image = featureCollection.reduceToImage(properties=['POP'], reducer=ee.Reducer.first()).rename('den')
    return image

def get_tile_url(image, bands, min, max):
    vis_params = {
        'bands': bands,
        'min': min,
        'max': max
    }
    image_viz = image.visualize(**vis_params)
    map_id_dict = ee.data.getMapId({'image': image_viz})
    tile_url = map_id_dict['tile_fetcher'].url_format
    return(tile_url)

def read_json_or_empty(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError:
        # Return empty dict if file exists but is not valid JSON
        return {}

def update_tile_config(path='./config.json'):
    res = read_json_or_empty(path)
    MAP_TILES = {
        "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "S1 2021": get_tile_url(s1_2021(), ['VV'], -20, 1),
        "S2 2021 RGB": get_tile_url(s2_2021(), ['B4', 'B3', 'B2'], 0, 3000),
        "VIIRS 2021": get_tile_url(viirs_2021(), ['avg_rad'], 0, 60),
        "Census 1000 2021": get_tile_url(census_1000_2021(), ['den'], 0, 100),
        "Census 500 2021": get_tile_url(census_500_2021(), ['den'], 0, 100),
        "Census 250 2021": get_tile_url(census_250_2021(), ['den'], 0, 100),
        "Census 100 2021": get_tile_url(census_100_2021(), ['den'], 0, 100),
        "Census 2021": get_tile_url(census_2021(), ['den'], 0, 100)
    }
    res['MAP_TILES'] = MAP_TILES
    with open(path, 'w') as file:
        json.dump(res, file, indent=4)

def get_config(path='./config.json'):
    res = read_json_or_empty(path)
    return res

def get_rectangle_bounds(center, width_km=5, height_km=5):
    # Earth's radius in kilometers
    R = 6371
    # Convert km to degrees
    # 1 degree of latitude is approximately 111.32 km
    # 1 degree of longitude is approximately 111.32 * cos(latitude) km
    lat, lon = center
    # Calculate the change in latitude (constant)
    dlat = (height_km / 2) / 111.32
    # Calculate the change in longitude (varies with latitude)
    dlon = (width_km / 2) / (111.32 * math.cos(lat * math.pi / 180))
    return [
        [lat - dlat, lon - dlon],  # Southwest corner
        [lat + dlat, lon + dlon]   # Northeast corner
    ]

# -----------------------------------------------------------------------------------------
# FUNCTION FOR GETTING GEE IMAGE AS NP ARRAY
def take_500(matrix):
    x, y = matrix.shape
    x = (x - 500) // 2
    y = (y - 500) // 2
    matrix = matrix[x:x+500,y:y+500]
    return matrix

def take_500_(matrix):
    x, y, _ = matrix.shape
    x = (x - 500) // 2
    y = (y - 500) // 2
    matrix = matrix[x:x+500,y:y+500,:]
    return matrix

def ee_image_to_epsg3346(ee_image, scale=10):
    res = ee_image.reproject(crs='EPSG:3346', scale=scale)
    return res

def gee_image_to_np_image(ee_image, lat, lon, scale=10, bands=None):
    buffer = ee.Geometry.Point([lon, lat]).buffer(2600)
    ee_image = ee_image_to_epsg3346(ee_image, scale)
    if bands:
        url = ee_image.getDownloadURL({
            'scale': scale,
            'region': buffer.getInfo(),
            'format': 'NPY',
            'bands': bands
        })
    else:
        url = ee_image.getDownloadURL({
            'scale': scale,
            'region': buffer.getInfo(),
            'format': 'NPY'
        })
    response = requests.get(url)
    gee_arr = np.load(io.BytesIO(response.content), allow_pickle=True)
    return take_500(gee_arr)

def get_osm_image(lat, lon, radius_meters=2600, resolution_meters=10):
   size_pixels = int(2 * radius_meters / resolution_meters)
   zoom = min(19, int(math.log2(156543.03392 * math.cos(math.radians(lat)) / resolution_meters)))
   
   m = StaticMap(size_pixels, size_pixels)
   image = m.render(zoom=zoom, center=(lon, lat))
   
   return take_500_(np.array(image))

def save_np(array, path):
    np.save(path, array)

init_gee()

#gee_s1 = s1_2021()
#res = gee_image_to_np_image(gee_s1, 54.8985, 23.9036)
#update_tile_config()