import matplotlib.pyplot as plt
import pandas as pd

import numpy as np
from datetime import date, timedelta
import folium

from sentinelhub import (
    SHConfig,
    DataCollection,
    SentinelHubCatalog,
    SentinelHubRequest,
    SentinelHubStatistical,
    BBox,
    bbox_to_dimensions,
    CRS,
    MimeType,
    Geometry,
)

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


from extern import utils




client_id = 'sh-dc470478-1d88-4abf-928f-1270585855a2'
client_secret = '3SR5S3Mas5MkJYx7qfRlSsUUsTEiug8Q'


config = SHConfig()
config.sh_client_id = 'sh-dc470478-1d88-4abf-928f-1270585855a2'
config.sh_client_secret = '3SR5S3Mas5MkJYx7qfRlSsUUsTEiug8Q'
config.sh_base_url = 'https://sh.dataspace.copernicus.eu'
config.sh_token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'

today = date.today()
one_week_ago = today - timedelta(weeks=1)
time_interval = (one_week_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))

IMG_SIZE = 2450


evalscript_true_color = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04"]
            }],
            output: {
                bands: 3
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02];
    }
"""



def getFieldBBox(lat: float, lon:float, res: float):
    ext = (IMG_SIZE/2) * (res/1000)
    lat_min = float(lat) - ext/111
    lat_max = float(lat) + ext/111
    lon_min = float(lon) - ext/111
    lon_max = float(lon) + ext/111
    return [lon_min, lat_min, lon_max, lat_max]



def getSearchIterator(catalog, aoi_bbox: list[float], time_interval):
    search_iterator = catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=aoi_bbox,
        time=time_interval,
        fields={"include": ["id", "properties.datetime"], "exclude": []},
    )
    return search_iterator


def getImage(aoi: list[float], time_interval: tuple, res: int = 10):
    aoi_bbox = BBox(bbox=aoi, crs=CRS.WGS84)
    aoi_size = bbox_to_dimensions(aoi_bbox, resolution=res)
    catalog = SentinelHubCatalog(config=config)

    search_iterator = getSearchIterator(catalog, aoi_bbox, time_interval)
    # results = list(search_iterator)

    request_true_color = SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    name="s2l2a", service_url="https://sh.dataspace.copernicus.eu"
                ),
                time_interval=time_interval,
                other_args={"dataFilter": {"mosaickingOrder": "leastCC"}},
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=aoi_bbox,
        size=aoi_size,
        config=config,
    )
    true_color_imgs = request_true_color.get_data()
    return true_color_imgs[0]


def getMap(image, aoi: list):
    map = folium.Map(location=[(aoi[1] + aoi[3]) / 2, (aoi[0] + aoi[2]) / 2], zoom_start=15)
    folium.raster_layers.ImageOverlay(
        image=image,
        bounds=[[aoi[1], aoi[0]], [aoi[3], aoi[2]]],
        opacity=1,
    ).add_to(map)
    return map


###########################################################################################
######################################### Evalcripts#######################################
###########################################################################################

evalscript_ndvi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B04",
        "B08",
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  }
}
  

function evaluatePixel(sample) {
    let val = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    let imgVals = null;
    
    if (val<-1.1) imgVals = [0,0,0];
    else if (val<-0.2) imgVals = [0.75,0.75,0.75];
    else if (val<-0.1) imgVals = [0.86,0.86,0.86];
    else if (val<0) imgVals = [1,1,0.88];
    else if (val<0.025) imgVals = [1,0.98,0.8];
    else if (val<0.05) imgVals = [0.93,0.91,0.71];
    else if (val<0.075) imgVals = [0.87,0.85,0.61];
    else if (val<0.1) imgVals = [0.8,0.78,0.51];
    else if (val<0.125) imgVals = [0.74,0.72,0.42];
    else if (val<0.15) imgVals = [0.69,0.76,0.38];
    else if (val<0.175) imgVals = [0.64,0.8,0.35];
    else if (val<0.2) imgVals = [0.57,0.75,0.32];
    else if (val<0.25) imgVals = [0.5,0.7,0.28];
    else if (val<0.3) imgVals = [0.44,0.64,0.25];
    else if (val<0.35) imgVals = [0.38,0.59,0.21];
    else if (val<0.4) imgVals = [0.31,0.54,0.18];
    else if (val<0.45) imgVals = [0.25,0.49,0.14];
    else if (val<0.5) imgVals = [0.19,0.43,0.11];
    else if (val<0.55) imgVals = [0.13,0.38,0.07];
    else if (val<0.6) imgVals = [0.06,0.33,0.04];
    else imgVals = [0,0.27,0];
    
    
    imgVals.push(sample.dataMask)
    
    return imgVals
}
"""



evalscript_arvi = """ 
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B02",  // Blue band
        "B04",  // Red band
        "B08",  // NIR band
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  }
}

function evaluatePixel(sample) {
    // ARVI formula
    let gamma = 1.0;  // Correction factor
    let correctedRed = sample.B04 - gamma * (sample.B04 - sample.B02);
    let val = (sample.B08 - correctedRed) / (sample.B08 + correctedRed);
    
    let imgVals = null;

    // Visualization based on ARVI values
    if (val < -1.1) imgVals = [0, 0, 0];
    else if (val < -0.2) imgVals = [0.75, 0.75, 0.75];
    else if (val < -0.1) imgVals = [0.86, 0.86, 0.86];
    else if (val < 0) imgVals = [1, 1, 0.88];
    else if (val < 0.025) imgVals = [1, 0.98, 0.8];
    else if (val < 0.05) imgVals = [0.93, 0.91, 0.71];
    else if (val < 0.075) imgVals = [0.87, 0.85, 0.61];
    else if (val < 0.1) imgVals = [0.8, 0.78, 0.51];
    else if (val < 0.125) imgVals = [0.74, 0.72, 0.42];
    else if (val < 0.15) imgVals = [0.69, 0.76, 0.38];
    else if (val < 0.175) imgVals = [0.64, 0.8, 0.35];
    else if (val < 0.2) imgVals = [0.57, 0.75, 0.32];
    else if (val < 0.25) imgVals = [0.5, 0.7, 0.28];
    else if (val < 0.3) imgVals = [0.44, 0.64, 0.25];
    else if (val < 0.35) imgVals = [0.38, 0.59, 0.21];
    else if (val < 0.4) imgVals = [0.31, 0.54, 0.18];
    else if (val < 0.45) imgVals = [0.25, 0.49, 0.14];
    else if (val < 0.5) imgVals = [0.19, 0.43, 0.11];
    else if (val < 0.55) imgVals = [0.13, 0.38, 0.07];
    else if (val < 0.6) imgVals = [0.06, 0.33, 0.04];
    else imgVals = [0, 0.27, 0];
    
    imgVals.push(sample.dataMask);
    return imgVals;
}
"""

evalscript_evi = """ 
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B02", // Blue
        "B04", // Red
        "B08", // NIR
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    let G = 2.5;
    let C1 = 6.0;
    let C2 = 7.5;
    let L = 1.0;

    let evi = G * (sample.B08 - sample.B04) / (sample.B08 + C1 * sample.B04 - C2 * sample.B02 + L);

    let imgVals = null;

    if (evi < -1.1) imgVals = [0, 0, 0];
    else if (evi < -0.2) imgVals = [0.75, 0.75, 0.75];
    else if (evi < -0.1) imgVals = [0.86, 0.86, 0.86];
    else if (evi < 0) imgVals = [1, 1, 0.88];
    else if (evi < 0.025) imgVals = [1, 0.98, 0.8];
    else if (evi < 0.05) imgVals = [0.93, 0.91, 0.71];
    else if (evi < 0.075) imgVals = [0.87, 0.85, 0.61];
    else if (evi < 0.1) imgVals = [0.8, 0.78, 0.51];
    else if (evi < 0.125) imgVals = [0.74, 0.72, 0.42];
    else if (evi < 0.15) imgVals = [0.69, 0.76, 0.38];
    else if (evi < 0.175) imgVals = [0.64, 0.8, 0.35];
    else if (evi < 0.2) imgVals = [0.57, 0.75, 0.32];
    else if (evi < 0.25) imgVals = [0.5, 0.7, 0.28];
    else if (evi < 0.3) imgVals = [0.44, 0.64, 0.25];
    else if (evi < 0.35) imgVals = [0.38, 0.59, 0.21];
    else if (evi < 0.4) imgVals = [0.31, 0.54, 0.18];
    else if (evi < 0.45) imgVals = [0.25, 0.49, 0.14];
    else if (evi < 0.5) imgVals = [0.19, 0.43, 0.11];
    else if (evi < 0.55) imgVals = [0.13, 0.38, 0.07];
    else if (evi < 0.6) imgVals = [0.06, 0.33, 0.04];
    else imgVals = [0, 0.27, 0];

    imgVals.push(sample.dataMask);

    return imgVals;
} """
