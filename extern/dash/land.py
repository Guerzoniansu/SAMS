import matplotlib.pyplot as plt
import pandas as pd

import numpy as np
from datetime import date, timedelta
import folium
from prophet import Prophet
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Span, Legend
from bokeh.embed import components
from bokeh.colors import named
from bokeh.palettes import Spectral11

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

from datetime import datetime

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


from extern import utils
from extern.dash import analysis as a
from extern.dash import cste
from extern.dash.dt import dtmaker as dtm




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


###########################################################################################
######################################### Evalcripts#######################################
###########################################################################################


evalscript_default = """
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


evalscript_ndvi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
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
    // Calculate NDVI
    let numerator = sample.B08 - sample.B04;
    let denominator = sample.B08 + sample.B04;
    let ndvi = denominator !== 0 ? numerator / denominator : -1;

    // Visualization based on NDVI values
    let imgVals = null;

    if (ndvi < 0.0) imgVals = [0.5, 0.5, 0.5]; // Bare soil or non-vegetation (gray)
    else if (ndvi < 0.2) imgVals = [1, 0.8, 0.6]; // Sparse vegetation (light orange)
    else if (ndvi < 0.4) imgVals = [0.8, 1, 0.5]; // Moderate vegetation (yellow-green)
    else if (ndvi < 0.6) imgVals = [0.4, 0.9, 0.4]; // Dense vegetation (green)
    else if (ndvi < 0.8) imgVals = [0.1, 0.7, 0.1]; // Very dense vegetation (dark green)
    else imgVals = [0, 0.4, 0]; // Extremely dense vegetation (deep green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
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
    if (val < -0.5) imgVals = [0, 0, 0]; // Very low ARVI (black)
    else if (val < -0.2) imgVals = [0.5, 0.5, 0.5]; // Bare soil (gray)
    else if (val < 0.0) imgVals = [1, 0.8, 0.6]; // Sparse vegetation (light orange)
    else if (val < 0.2) imgVals = [1, 1, 0.4]; // Moderately sparse vegetation (yellow)
    else if (val < 0.4) imgVals = [0.6, 0.9, 0.3]; // Moderate vegetation (light green)
    else if (val < 0.6) imgVals = [0.3, 0.7, 0.2]; // Dense vegetation (green)
    else if (val < 0.8) imgVals = [0.1, 0.5, 0.1]; // Very dense vegetation (dark green)
    else imgVals = [0, 0.3, 0]; // Extremely dense vegetation (deep green)
    
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

    let numerator = G * (sample.B08 - sample.B04);
    let denominator = (sample.B08 + C1 * sample.B04 - C2 * sample.B02 + L);
    let val = denominator !== 0 ? numerator / denominator : -1;

    let imgVals = null;

    if (val < -0.2) imgVals = [0, 0, 0]; // Invalid or very low EVI (black)
    else if (val < 0.0) imgVals = [0.5, 0.5, 0.5]; // Bare soil (gray)
    else if (val < 0.2) imgVals = [1, 0.8, 0.6]; // Sparse vegetation (light orange)
    else if (val < 0.4) imgVals = [0.8, 1, 0.5]; // Moderate vegetation (yellow-green)
    else if (val < 0.6) imgVals = [0.4, 0.9, 0.4]; // Dense vegetation (green)
    else if (val < 0.8) imgVals = [0.1, 0.7, 0.1]; // Very dense vegetation (dark green)
    else imgVals = [0, 0.4, 0]; // Extremely dense vegetation (deep green)

    imgVals.push(sample.dataMask);

    return imgVals;
} """



evalscript_lai = """
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
    // Constants for EVI calculation
    let G = 2.5;
    let C1 = 6.0;
    let C2 = 7.5;
    let L = 1.0;

    // Calculate EVI
    let numerator = G * (sample.B08 - sample.B04);
    let denominator = (sample.B08 + C1 * sample.B04 - C2 * sample.B02 + L);
    let evi = denominator !== 0 ? numerator / denominator : -1;

    // Convert EVI to LAI using linear regression (example coefficients)
    let a = 3.0; // Scaling factor
    let b = 0.5; // Offset
    let lai = evi > 0 ? a * evi + b : 0;

    // Visualization based on LAI values
    let imgVals = null;
    if (lai < 1) imgVals = [0.8, 0.8, 0.8]; // Bare soil (gray)
    else if (lai < 2) imgVals = [1, 0.9, 0.6]; // Sparse vegetation (light orange)
    else if (lai < 3) imgVals = [0.8, 1, 0.4]; // Moderate vegetation (yellow-green)
    else if (lai < 4) imgVals = [0.4, 0.9, 0.4]; // Dense vegetation (green)
    else if (lai < 5) imgVals = [0.1, 0.7, 0.1]; // Very dense vegetation (dark green)
    else imgVals = [0, 0.5, 0]; // Extremely dense vegetation (deep green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}
"""



evalscript_nbr = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B08", // NIR
        "B12", // SWIR
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate NBR
    let numerator = sample.B08 - sample.B12;
    let denominator = sample.B08 + sample.B12;
    let nbr = denominator !== 0 ? numerator / denominator : -1;

    // Visualization based on NBR values
    let imgVals = null;

    if (nbr < -0.1) imgVals = [0.6, 0.4, 0.2]; // Burned areas (brown)
    else if (nbr < 0.1) imgVals = [1, 0.8, 0.6]; // Bare soil or sparse vegetation (light orange)
    else if (nbr < 0.3) imgVals = [0.8, 1, 0.5]; // Moderately healthy vegetation (yellow-green)
    else if (nbr < 0.5) imgVals = [0.4, 0.9, 0.4]; // Healthy vegetation (green)
    else imgVals = [0.1, 0.7, 0.1]; // Very healthy vegetation (dark green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}
"""

evalscript_gndvi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B03", // Green
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
    // Calculate GNDVI
    let numerator = sample.B08 - sample.B03;
    let denominator = sample.B08 + sample.B03;
    let gndvi = denominator !== 0 ? numerator / denominator : -1;

    // Visualization based on GNDVI values
    let imgVals = null;

    if (gndvi < 0.2) imgVals = [0.5, 0.5, 0.5]; // Bare soil or sparse vegetation (gray)
    else if (gndvi < 0.4) imgVals = [1, 0.8, 0.6]; // Moderately sparse vegetation (light orange)
    else if (gndvi < 0.6) imgVals = [0.8, 1, 0.5]; // Moderate vegetation (yellow-green)
    else if (gndvi < 0.8) imgVals = [0.4, 0.9, 0.4]; // Dense vegetation (green)
    else imgVals = [0.1, 0.7, 0.1]; // Very dense vegetation (dark green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""

evalscript_ndmi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B08", // NIR
        "B11", // SWIR
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate NDMI
    let numerator = sample.B08 - sample.B11;
    let denominator = sample.B08 + sample.B11;
    let ndmi = denominator !== 0 ? numerator / denominator : -1;

    // Visualization based on NDMI values
    let imgVals = null;

    if (ndmi < -0.2) imgVals = [0.4, 0.2, 0.1]; // Very low moisture (brown)
    else if (ndmi < 0.0) imgVals = [0.6, 0.4, 0.2]; // Low moisture (light brown)
    else if (ndmi < 0.2) imgVals = [0.8, 0.7, 0.4]; // Moderate moisture (yellow)
    else if (ndmi < 0.4) imgVals = [0.4, 0.8, 0.4]; // Healthy vegetation (green)
    else if (ndmi < 0.6) imgVals = [0.2, 0.6, 0.2]; // High moisture (dark green)
    else imgVals = [0.1, 0.4, 0.1]; // Very high moisture (deep green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""


evalscript_ndre = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B08", // NIR
        "B05", // RedEdge
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate NDRE
    let numerator = sample.B08 - sample.B05;
    let denominator = sample.B08 + sample.B05;
    let ndre = denominator !== 0 ? numerator / denominator : -1;

    // Visualization based on NDRE values
    let imgVals = null;

    if (ndre < -0.2) imgVals = [0.4, 0.2, 0.1]; // Very low NDRE (brown)
    else if (ndre < 0.0) imgVals = [0.6, 0.4, 0.2]; // Low NDRE (light brown)
    else if (ndre < 0.2) imgVals = [1, 0.8, 0.4]; // Moderate vegetation (yellow)
    else if (ndre < 0.4) imgVals = [0.6, 0.9, 0.4]; // Healthy vegetation (light green)
    else if (ndre < 0.6) imgVals = [0.3, 0.7, 0.3]; // Very healthy vegetation (green)
    else imgVals = [0.1, 0.5, 0.1]; // Extremely healthy vegetation (dark green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""


evalscript_reci = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B08", // NIR
        "B05", // RedEdge
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate RECI
    let reci = (sample.B08 / sample.B05) - 1;

    // Visualization based on RECI values
    let imgVals = null;

    if (reci < 0.5) imgVals = [0.5, 0.2, 0.1]; // Low chlorophyll (brown)
    else if (reci < 1.0) imgVals = [0.7, 0.5, 0.3]; // Moderate chlorophyll (orange)
    else if (reci < 1.5) imgVals = [1, 0.8, 0.4]; // Healthy vegetation (yellow)
    else if (reci < 2.0) imgVals = [0.6, 0.9, 0.4]; // Very healthy vegetation (light green)
    else if (reci < 2.5) imgVals = [0.3, 0.7, 0.2]; // High chlorophyll (green)
    else imgVals = [0.1, 0.5, 0.1]; // Extremely high chlorophyll (dark green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""

evalscript_savi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B08", // NIR
        "B04", // Red
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Set the soil adjustment factor
    let L = 0.5; // Default value for SAVI

    // Calculate SAVI
    let savi = ((sample.B08 - sample.B04) * (1 + L)) / (sample.B08 + sample.B04 + L);

    // Visualization based on SAVI values
    let imgVals = null;

    if (savi < -0.3) imgVals = [0.5, 0.2, 0.1]; // Very low SAVI (brown)
    else if (savi < 0.0) imgVals = [0.6, 0.4, 0.2]; // Low SAVI (light brown)
    else if (savi < 0.2) imgVals = [1, 0.8, 0.4]; // Sparse vegetation (orange)
    else if (savi < 0.4) imgVals = [0.8, 1, 0.5]; // Moderate vegetation (yellow-green)
    else if (savi < 0.6) imgVals = [0.4, 0.9, 0.4]; // Healthy vegetation (green)
    else if (savi < 0.8) imgVals = [0.2, 0.7, 0.2]; // Very healthy vegetation (dark green)
    else imgVals = [0.1, 0.5, 0.1]; // Extremely healthy vegetation (deep green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""


evalscript_osavi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B08", // NIR
        "B04", // Red
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate OSAVI
    let osavi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04 + 0.16);

    // Visualization based on OSAVI values
    let imgVals = null;

    if (osavi < -0.3) imgVals = [0.5, 0.2, 0.1]; // Very low OSAVI (brown)
    else if (osavi < 0.0) imgVals = [0.6, 0.4, 0.2]; // Low OSAVI (light brown)
    else if (osavi < 0.2) imgVals = [1, 0.8, 0.4]; // Sparse vegetation (orange)
    else if (osavi < 0.4) imgVals = [0.8, 1, 0.5]; // Moderate vegetation (yellow-green)
    else if (osavi < 0.6) imgVals = [0.4, 0.9, 0.4]; // Healthy vegetation (green)
    else if (osavi < 0.8) imgVals = [0.2, 0.7, 0.2]; // Very healthy vegetation (dark green)
    else imgVals = [0.1, 0.5, 0.1]; // Extremely healthy vegetation (deep green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""



evalscript_msavi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B08", // NIR
        "B04", // Red
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate MSAVI
    let msavi = (2 * sample.B08 + 1 - Math.sqrt(Math.pow((2 * sample.B08 + 1), 2) - 8 * (sample.B08 - sample.B04))) / 2;

    // Visualization based on MSAVI values
    let imgVals = null;

    if (msavi < -0.2) imgVals = [0.5, 0.2, 0.1]; // Very low MSAVI (brown)
    else if (msavi < 0.0) imgVals = [0.6, 0.4, 0.2]; // Low MSAVI (light brown)
    else if (msavi < 0.2) imgVals = [1, 0.8, 0.4]; // Sparse vegetation (orange)
    else if (msavi < 0.4) imgVals = [0.8, 1, 0.5]; // Moderate vegetation (yellow-green)
    else if (msavi < 0.6) imgVals = [0.4, 0.9, 0.4]; // Healthy vegetation (green)
    else if (msavi < 0.8) imgVals = [0.2, 0.7, 0.2]; // Very healthy vegetation (dark green)
    else imgVals = [0.1, 0.5, 0.1]; // Extremely healthy vegetation (deep green)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""


evalscript_sipi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B04", // Red band
        "B05", // Red-edge band (example, may vary by sensor)
        "B08", // NIR band
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate SIPI
    let sipi = (sample.B08 - sample.B05) / (sample.B08 - sample.B04);

    // Visualization based on SIPI values
    let imgVals = null;

    if (sipi < -0.5) imgVals = [0.5, 0.1, 0.1]; // Very low SIPI (brown, indicating unhealthy vegetation)
    else if (sipi < 0.0) imgVals = [0.6, 0.4, 0.2]; // Low SIPI (yellow, stressed vegetation)
    else if (sipi < 0.2) imgVals = [0.8, 0.7, 0.2]; // Medium SIPI (light green, moderately healthy vegetation)
    else if (sipi < 0.4) imgVals = [0.4, 0.9, 0.4]; // High SIPI (green, healthy vegetation)
    else if (sipi < 0.6) imgVals = [0.2, 0.7, 0.2]; // Very high SIPI (dark green, very healthy vegetation)
    else imgVals = [0.1, 0.5, 0.1]; // Extremely high SIPI (deep green, optimal chlorophyll content)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""


evalscript_gci = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B03", // Green band
        "B08", // NIR band
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate GCI
    let gci = (sample.B08 - sample.B03) / (sample.B03 + 1);

    // Visualization based on GCI values
    let imgVals = null;

    if (gci < -0.5) imgVals = [0.5, 0.1, 0.1]; // Very low GCI (brown, indicating unhealthy vegetation)
    else if (gci < 0.0) imgVals = [0.6, 0.4, 0.2]; // Low GCI (yellow, stressed vegetation)
    else if (gci < 0.2) imgVals = [0.8, 0.7, 0.2]; // Medium GCI (light green, moderately healthy vegetation)
    else if (gci < 0.4) imgVals = [0.4, 0.9, 0.4]; // High GCI (green, healthy vegetation)
    else if (gci < 0.6) imgVals = [0.2, 0.7, 0.2]; // Very high GCI (dark green, very healthy vegetation)
    else imgVals = [0.1, 0.5, 0.1]; // Extremely high GCI (deep green, optimal chlorophyll content)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""


evalscript_ndsi = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B03", // Green band
        "B11", // SWIR band
        "dataMask"
      ]
    }],
    output: {
      bands: 4
    }
  };
}

function evaluatePixel(sample) {
    // Calculate NDSI
    let ndsi = (sample.B03 - sample.B11) / (sample.B03 + sample.B11);

    // Visualization based on NDSI values
    let imgVals = null;

    if (ndsi < 0.0) imgVals = [0, 0, 1]; // Non-snow surfaces (blue, for water or bare land)
    else if (ndsi < 0.2) imgVals = [0.5, 0.5, 0.5]; // Low NDSI (gray, for mixed surfaces or sparse snow)
    else if (ndsi < 0.4) imgVals = [0.8, 0.8, 0.8]; // Intermediate NDSI (light gray, for snow-covered areas)
    else if (ndsi < 0.6) imgVals = [1, 1, 1]; // High NDSI (white, indicating fresh snow)
    else imgVals = [1, 1, 1]; // Very high NDSI (still white, indicating snow)

    imgVals.push(sample.dataMask); // Include dataMask for transparency

    return imgVals;
}

"""



def getFieldBBox(lat: float, lon:float, res: float):
    ext = (IMG_SIZE/2) * (res/1000)
    lat_min = float(lat) - ext/111
    lat_max = float(lat) + ext/111
    lon_min = float(lon) - ext/111
    lon_max = float(lon) + ext/111
    return [lon_min, lat_min, lon_max, lat_max]


def getEvalScript(param: str):
    if param == "default":
        return evalscript_default
    elif param == "arvi":
        return evalscript_arvi
    elif param == "evi":
        return evalscript_evi
    elif param == "lai":
        return evalscript_lai
    elif param == "nbr":
        return evalscript_nbr
    elif param == "ndvi":
        return evalscript_ndvi
    elif param == "gndvi":
        return evalscript_gndvi
    elif param == "ndmi":
        return evalscript_ndmi
    elif param == "ndre":
        return evalscript_ndre
    elif param == "reci":
        return evalscript_reci
    elif param == "savi":
        return evalscript_savi
    elif param == "osavi":
        return evalscript_osavi
    elif param == "msavi":
        return evalscript_msavi
    elif param == "sipi":
        return evalscript_sipi
    elif param == "gci":
        return evalscript_gci
    elif param == "ndsi":
        return evalscript_ndsi
    else:
        raise ValueError("Unsupported parameter: " + param)



def getSearchIterator(catalog, aoi_bbox: list[float], time_interval):
    search_iterator = catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=aoi_bbox,
        time=time_interval,
        fields={"include": ["id", "properties.datetime"], "exclude": []},
    )
    return search_iterator


def getImage(aoi: list[float], param: str, time_interval: tuple, res: int = 10):
    aoi_bbox = BBox(bbox=aoi, crs=CRS.WGS84)
    aoi_size = bbox_to_dimensions(aoi_bbox, resolution=res)
    catalog = SentinelHubCatalog(config=config)

    search_iterator = getSearchIterator(catalog, aoi_bbox, time_interval)
    es = getEvalScript(param=param)
    # results = list(search_iterator)

    request_true_color = SentinelHubRequest(
        evalscript=es,
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
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite",
        overlay=False,
        control=True
    ).add_to(map)
    folium.raster_layers.ImageOverlay(
        image=image,
        bounds=[[aoi[1], aoi[0]], [aoi[3], aoi[2]]],
        opacity=1,
    ).add_to(map)
    folium.Rectangle(
        bounds=[[aoi[1], aoi[0]], [aoi[3], aoi[2]]],  # Coordinates of the bounding box
        color="orange",  # Color of the rectangle
        weight=4,     # Line thickness
        fill=False    # Set to False to make it a simple outline
    ).add_to(map)
    return map



def calculateCloudCover(aoi: list[float], time_interval: tuple, res: int = 10, cloud_threshold: int = 50) -> float:
    """
    Calculate the cloud cover percentage for a Sentinel-2 image over a given area of interest (AOI).
    
    Parameters:
        aoi (list[float]): The bounding box of the area of interest [min_lon, min_lat, max_lon, max_lat].
        time_interval (tuple): Date range for the image retrieval (e.g., ("2023-01-01", "2023-01-15")).
        res (int): Spatial resolution of the image in meters per pixel (default: 10).
        cloud_threshold (int): Cloud probability threshold percentage (default: 50%).
    
    Returns:
        float: Cloud cover percentage.
    """
    from sentinelhub import BBox, CRS, bbox_to_dimensions, SentinelHubRequest, DataCollection, MimeType

    # Define AOI and resolution
    aoi_bbox = BBox(bbox=aoi, crs=CRS.WGS84)
    aoi_size = bbox_to_dimensions(aoi_bbox, resolution=res)

    # Evalscript to retrieve only the CLP (cloud probability) band
    eval_script = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["CLP"],
                units: "DN"
            }],
            output: {
                bands: 1,
                sampleType: "FLOAT32"
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.CLP / 255]; // Normalize CLP band to [0, 1]
    }
    """

    # SentinelHub request for the CLP band
    request = SentinelHubRequest(
        evalscript=eval_script,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    name="s2l2a", service_url="https://sh.dataspace.copernicus.eu"
                ),
                time_interval=time_interval,
                other_args={"dataFilter": {"mosaickingOrder": "leastCC"}},
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=aoi_bbox,
        size=aoi_size,
        config=config,
    )

    # Fetch the CLP data
    clp_data = request.get_data()
    cloud_probability = clp_data[0][:, :, 0]  # Extract the CLP band

    # Calculate cloud cover percentage
    total_pixels = cloud_probability.size
    cloudy_pixels = (cloud_probability > cloud_threshold / 100).sum()
    cloud_cover_percentage = (cloudy_pixels / total_pixels) * 100

    return cloud_cover_percentage




def getHtmlLegend(param: str):
    if param == "default":
        return """<p>Base map of your farm</p>"""
    elif param == "arvi":
        return """
            <!DOCTYPE html>
              <html lang="en">
              <head>
                  <meta charset="UTF-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <link rel="preconnect" href="https://fonts.googleapis.com">
                  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                  <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
                  <style>
                      .legend {
                          font-size: 14px;
                          font-family: 'Lato', sans-serif;
                      }
                      .legend-item {
                          display: flex;
                          align-items: center;
                          margin-bottom: 5px;
                      }
                      .legend-color {
                          width: 20px;
                          height: 20px;
                          margin-right: 10px;
                          border: 1px solid #000;
                      }
                  </style>
              </head>
              <body>
                  <div class="legend">
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(0, 0, 0);"></div>
                          <span>Very low ARVI: &lt; -0.5</span>
                      </div>
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(128, 128, 128);"></div>
                          <span>Bare soil: -0.5 to -0.2</span>
                      </div>
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(255, 204, 153);"></div>
                          <span>Sparse vegetation: -0.2 to 0.0</span>
                      </div>
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(255, 255, 102);"></div>
                          <span>Moderately sparse vegetation: 0.0 to 0.2</span>
                      </div>
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(153, 230, 77);"></div>
                          <span>Moderate vegetation: 0.2 to 0.4</span>
                      </div>
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(77, 179, 51);"></div>
                          <span>Dense vegetation: 0.4 to 0.6</span>
                      </div>
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(26, 128, 26);"></div>
                          <span>Very dense vegetation: 0.6 to 0.8</span>
                      </div>
                      <div class="legend-item">
                          <div class="legend-color" style="background-color: rgb(0, 77, 0);"></div>
                          <span>Extremely dense vegetation: &gt; 0.8</span>
                      </div>
                  </div>
              </body>
              </html>
            """
    elif param == "evi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
  <style>
      .legend {
          font-size: 14px;
          font-family: 'Lato', sans-serif;
      }
      .legend-item {
          display: flex;
          align-items: center;
          margin-bottom: 5px;
      }
      .legend-color {
          width: 20px;
          height: 20px;
          margin-right: 10px;
          border: 1px solid #000;
      }
  </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(0, 0, 0);"></div>
            <span>Invalid or very low EVI: EVI &lt; -0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(128, 128, 128);"></div>
            <span>Bare soil: -0.2 ≤ EVI &lt; 0.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 153);"></div>
            <span>Sparse vegetation: 0.0 ≤ EVI &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 128);"></div>
            <span>Moderate vegetation: 0.2 ≤ EVI &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Dense vegetation: 0.4 ≤ EVI &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 179, 26);"></div>
            <span>Very dense vegetation: 0.6 ≤ EVI &lt; 0.8</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(0, 102, 0);"></div>
            <span>Extremely dense vegetation: EVI ≥ 0.8</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "lai":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 204, 204);"></div>
            <span>Bare soil: LAI &lt; 1</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 230, 153);"></div>
            <span>Sparse vegetation: 1 ≤ LAI &lt; 2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 102);"></div>
            <span>Moderate vegetation: 2 ≤ LAI &lt; 3</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Dense vegetation: 3 ≤ LAI &lt; 4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 179, 26);"></div>
            <span>Very dense vegetation: 4 ≤ LAI &lt; 5</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(0, 128, 0);"></div>
            <span>Extremely dense vegetation: LAI ≥ 5</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "nbr":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Burned areas: NBR &lt; -0.1</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 153);"></div>
            <span>Bare soil or sparse vegetation: -0.1 ≤ NBR &lt; 0.1</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 128);"></div>
            <span>Moderately healthy vegetation: 0.1 ≤ NBR &lt; 0.3</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Healthy vegetation: 0.3 ≤ NBR &lt; 0.5</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 179, 26);"></div>
            <span>Very healthy vegetation: NBR ≥ 0.5</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "ndvi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(128, 128, 128);"></div>
            <span>Bare soil or non-vegetation: NDVI &lt; 0.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 153);"></div>
            <span>Sparse vegetation: 0.0 ≤ NDVI &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 128);"></div>
            <span>Moderate vegetation: 0.2 ≤ NDVI &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Dense vegetation: 0.4 ≤ NDVI &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 179, 26);"></div>
            <span>Very dense vegetation: 0.6 ≤ NDVI &lt; 0.8</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(0, 102, 0);"></div>
            <span>Extremely dense vegetation: NDVI ≥ 0.8</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "gndvi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(128, 128, 128);"></div>
            <span>Bare soil or sparse vegetation: GNDVI &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 153);"></div>
            <span>Moderately sparse vegetation: 0.2 ≤ GNDVI &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 128);"></div>
            <span>Moderate vegetation: 0.4 ≤ GNDVI &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Dense vegetation: 0.6 ≤ GNDVI &lt; 0.8</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 179, 26);"></div>
            <span>Very dense vegetation: GNDVI ≥ 0.8</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "ndmi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 51, 26);"></div>
            <span>Very low moisture: NDMI &lt; -0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Low moisture: -0.2 ≤ NDMI &lt; 0.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 179, 102);"></div>
            <span>Moderate moisture: 0.0 ≤ NDMI &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 204, 102);"></div>
            <span>Healthy vegetation: 0.2 ≤ NDMI &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(51, 153, 51);"></div>
            <span>High moisture: 0.4 ≤ NDMI &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 102, 26);"></div>
            <span>Very high moisture: NDMI ≥ 0.6</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "ndre":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 51, 26);"></div>
            <span>Very low NDRE: NDRE &lt; -0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Low NDRE: -0.2 ≤ NDRE &lt; 0.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 102);"></div>
            <span>Moderate vegetation: 0.0 ≤ NDRE &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 230, 102);"></div>
            <span>Healthy vegetation: 0.2 ≤ NDRE &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(77, 179, 77);"></div>
            <span>Very healthy vegetation: 0.4 ≤ NDRE &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 128, 26);"></div>
            <span>Extremely healthy vegetation: NDRE ≥ 0.6</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "reci":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(127, 51, 26);"></div>
            <span>Low chlorophyll: RECI &lt; 0.5</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(178, 127, 76);"></div>
            <span>Moderate chlorophyll: 0.5 ≤ RECI &lt; 1.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 102);"></div>
            <span>Healthy vegetation: 1.0 ≤ RECI &lt; 1.5</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 230, 102);"></div>
            <span>Very healthy vegetation: 1.5 ≤ RECI &lt; 2.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(77, 179, 77);"></div>
            <span>High chlorophyll: 2.0 ≤ RECI &lt; 2.5</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 128, 26);"></div>
            <span>Extremely high chlorophyll: RECI ≥ 2.5</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "savi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(127, 51, 26);"></div>
            <span>Very low SAVI: SAVI &lt; -0.3</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Low SAVI: -0.3 ≤ SAVI &lt; 0.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 102);"></div>
            <span>Sparse vegetation: 0.0 ≤ SAVI &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 102);"></div>
            <span>Moderate vegetation: 0.2 ≤ SAVI &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Healthy vegetation: 0.4 ≤ SAVI &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(51, 179, 51);"></div>
            <span>Very healthy vegetation: 0.6 ≤ SAVI &lt; 0.8</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 128, 26);"></div>
            <span>Extremely healthy vegetation: SAVI ≥ 0.8</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "osavi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(127, 51, 26);"></div>
            <span>Very low OSAVI: OSAVI &lt; -0.3</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Low OSAVI: -0.3 ≤ OSAVI &lt; 0.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 102);"></div>
            <span>Sparse vegetation: 0.0 ≤ OSAVI &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 102);"></div>
            <span>Moderate vegetation: 0.2 ≤ OSAVI &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Healthy vegetation: 0.4 ≤ OSAVI &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(51, 179, 51);"></div>
            <span>Very healthy vegetation: 0.6 ≤ OSAVI &lt; 0.8</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 128, 26);"></div>
            <span>Extremely healthy vegetation: OSAVI ≥ 0.8</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "msavi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(127, 51, 26);"></div>
            <span>Very low MSAVI: MSAVI &lt; -0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Low MSAVI: -0.2 ≤ MSAVI &lt; 0.0</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 204, 102);"></div>
            <span>Sparse vegetation: 0.0 ≤ MSAVI &lt; 0.2</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 255, 102);"></div>
            <span>Moderate vegetation: 0.2 ≤ MSAVI &lt; 0.4</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>Healthy vegetation: 0.4 ≤ MSAVI &lt; 0.6</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(51, 179, 51);"></div>
            <span>Very healthy vegetation: 0.6 ≤ MSAVI &lt; 0.8</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 128, 26);"></div>
            <span>Extremely healthy vegetation: MSAVI ≥ 0.8</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "sipi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(127, 26, 13);"></div>
            <span>Very low SIPI: SIPI &lt; -0.5 (brown, unhealthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Low SIPI: -0.5 ≤ SIPI &lt; 0.0 (yellow, stressed vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 178, 51);"></div>
            <span>Medium SIPI: 0.0 ≤ SIPI &lt; 0.2 (light green, moderately healthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 204, 102);"></div>
            <span>High SIPI: 0.2 ≤ SIPI &lt; 0.4 (green, healthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(51, 153, 51);"></div>
            <span>Very high SIPI: 0.4 ≤ SIPI &lt; 0.6 (dark green, very healthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 128, 26);"></div>
            <span>Extremely high SIPI: SIPI ≥ 0.6 (deep green, optimal chlorophyll content)</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "gci":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(128, 25, 25);"></div>
            <span>Very low GCI: GCI &lt; -0.5 (brown, indicating unhealthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(153, 102, 51);"></div>
            <span>Low GCI: -0.5 ≤ GCI &lt; 0.0 (yellow, stressed vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 179, 51);"></div>
            <span>Medium GCI: 0.0 ≤ GCI &lt; 0.2 (light green, moderately healthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(102, 230, 102);"></div>
            <span>High GCI: 0.2 ≤ GCI &lt; 0.4 (green, healthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(51, 179, 51);"></div>
            <span>Very high GCI: 0.4 ≤ GCI &lt; 0.6 (dark green, very healthy vegetation)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(26, 127, 26);"></div>
            <span>Extremely high GCI: GCI ≥ 0.6 (deep green, optimal chlorophyll content)</span>
        </div>
    </div>
</body>
</html>

"""
    elif param == "ndsi":
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap" rel="stylesheet">
    <style>
        .legend {
            font-size: 14px;
            font-family: 'Lato', sans-serif;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #000;
        }
    </style>
</head>
<body>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(0, 0, 255);"></div>
            <span>Non-snow surfaces: NDSI &lt; 0.0 (blue, water or bare land)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(128, 128, 128);"></div>
            <span>Low NDSI: 0.0 ≤ NDSI &lt; 0.2 (gray, mixed surfaces or sparse snow)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(204, 204, 204);"></div>
            <span>Intermediate NDSI: 0.2 ≤ NDSI &lt; 0.4 (light gray, snow-covered areas)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 255, 255);"></div>
            <span>High NDSI: 0.4 ≤ NDSI &lt; 0.6 (white, fresh snow)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 255, 255);"></div>
            <span>Very high NDSI: NDSI ≥ 0.6 (still white, indicating snow)</span>
        </div>
    </div>
</body>
</html>

"""
    else:
        raise ValueError("Unsupported parameter: " + param)




def getTargetedParameter(param: str):
    if param == "default":
        return "Base View", "Image"
    elif param == "arvi":
        return "Atmospheric Resilience", "Burned Lands"
    elif param == "evi":
        return "Vegetation Density", "Late Season"
    elif param == "lai":
        return "Leaf Surface", "All Stages"
    elif param == "nbr":
        return "Farmyard Fires", "Crop Recovery"
    elif param == "ndvi":
        return "Active Biomass", "Middle Season"
    elif param == "gndvi":
        return "Chlorophyll Content", "Late Season"
    elif param == "ndmi":
        return "Water Content", "Irrigation / Drainage"
    elif param == "ndre":
        return "Chlorophyll Content", "Crop Development"
    elif param == "reci":
        return "Photosynthetic Activity", "Crop Development"
    elif param == "savi":
        return "Vegetation Density", "Initial Phase"
    elif param == "osavi":
        return "Vegetation Density", "Initial Phase"
    elif param == "msavi":
        return "Active Biomass", "Initial Phase"
    elif param == "sipi":
        return "Chlorophyll Content", "Crop Disease"
    elif param == "gci":
        return "Chlorophyll Content", "Seasons' Impact"
    elif param == "ndsi":
        return "Snow Cover", "Snow Mapping"
    else:
        raise ValueError("Unsupported parameter: " + param)



def getHtmlAdvice(param: str):
    if param == "default":
        return evalscript_default
    elif param == "arvi":
        return evalscript_arvi
    elif param == "evi":
        return evalscript_evi
    elif param == "lai":
        return evalscript_lai
    elif param == "nbr":
        return evalscript_nbr
    elif param == "ndvi":
        return evalscript_ndvi
    elif param == "gndvi":
        return evalscript_gndvi
    elif param == "ndmi":
        return evalscript_ndmi
    elif param == "ndre":
        return evalscript_ndre
    elif param == "reci":
        return evalscript_reci
    elif param == "savi":
        return evalscript_savi
    elif param == "osavi":
        return evalscript_osavi
    elif param == "msavi":
        return evalscript_msavi
    elif param == "sipi":
        return evalscript_sipi
    elif param == "gci":
        return evalscript_gci
    elif param == "ndsi":
        return evalscript_ndsi
    else:
        raise ValueError("Unsupported parameter: " + param)


# def getTodayEt0():
#   fcst_eto = a.getRadParamCampaignForecast(key = "data_rad", param="et0", campaign="cy")
#   today = date.today()
#   today_eto = fcst_eto.loc[fcst_eto['ds'] == pd.to_datetime(today), 'ET0'].values[0]
#   return today_eto

# def getWaterNeeds(crop: str, pld: str):
#     today_eto = getTodayEt0()
#     delta_days = (date.today() - pd.to_datetime(pld).date()).days
#     gsmax = cste.crop_data[crop]['gsmax']
#     kc = cste.crop_data[crop]["kc"]
#     cumulative_days = [sum(gsmax[:i+1]) for i in range(len(gsmax))]

#     # Determine the current stage
#     cs = None
#     for stage, max_days in enumerate(cumulative_days, start=1):
#         if delta_days <= max_days:
#             cs = stage
#             break
#         else:
#             continue
#     if cs:
#       if cs == 1:
#         sta = "Initial Phase"
#       elif cs == 2:
#         sta = "Crop Development Phase"
#       elif cs == 3:
#         sta = "Middle Season Stage"
#       else:
#         sta = "Late Season Stage"
#     else:
#         sta = "Post Harvest"
#         return 0, sta

#     return round(kc[cs - 1] * today_eto, 2), sta


def getRiceWaterNeeds():
    pass


def getParamCampaignForecast(key: str, param: str, tgp: int, pld: str):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    dt['ds'] = dt.index
    dt.rename(columns={param.upper(): 'y'}, inplace=True)
    
    ld = pd.to_datetime(pld).date()
    futures = pd.date_range(start=ld, end=ld + pd.Timedelta(days=1 + tgp), freq='D')
    futures = pd.DataFrame({'ds': futures})

    model = Prophet(growth="flat", seasonality_mode = 'additive')
    model.fit(dt)

    fcst = model.predict(futures)
    fcst = fcst[["ds", "yhat"]]
    # fcst = fcst[fcst['ds'] > dt['ds'].max()]
    fcst.rename(columns={'yhat': param.upper()}, inplace=True)
    return fcst


def getRadParamCampaignForecast(key: str, param: str, tgp: int, pld: str):
    dt = dtm.transformRadiationData(key)[[param.upper()]]
    dt['ds'] = dt.index
    dt.rename(columns={param.upper(): 'y'}, inplace=True)
    
    ld = pd.to_datetime(pld).date()
    futures = pd.date_range(start=ld, end=ld + pd.Timedelta(days=1 + tgp), freq='D')
    futures = pd.DataFrame({'ds': futures})

    model = Prophet(growth="flat", seasonality_mode = 'additive')
    model.fit(dt)

    fcst = model.predict(futures)
    fcst = fcst[["ds", "yhat"]]
    # fcst = fcst[fcst['ds'] > dt['ds'].max()]
    fcst.rename(columns={'yhat': param.upper()}, inplace=True)
    return fcst


def getForecastForCropDevelopment(tgp: int, pld: str, key: str = "data", key_rad = "data_rad"):
    fcstPrectotcorr = getParamCampaignForecast(key, "prectotcorr", tgp=tgp, pld=pld)
    fcstEt0 = getRadParamCampaignForecast(key_rad, param="et0", tgp=tgp, pld=pld)
    dt = pd.merge(fcstPrectotcorr, fcstEt0, on='ds', how='inner')
    return dt



def createCropDevelopmentDataFrame(start_date: str, crop: str, tgp: int = None):
    """
    Create a DataFrame for the crop development period, starting from a given date.

    Parameters:
        start_date (str): The starting date in 'YYYY-MM-DD' format.
        crop (str): The crop key.
        tgp (int): Total growth period.

    Returns:
        DataFrame: A DataFrame containing crop development details.
    """
    crop_info = cste.crop_data[crop]
    kc_stages = crop_info['kc']
    # stages = [round(tgp * kc/sum(kc_stages)) for kc in kc_stages]
    stages = crop_info.get('gsmax', [])
    tgp = crop_info['maxtgp']

    dt = getForecastForCropDevelopment(tgp, pld=start_date)
    dt['ds'] = pd.to_datetime(dt['ds']).dt.date

    # Filter data starting from the given start_date
    start_idx = dt[dt['ds'] == pd.to_datetime(start_date).date()].index[0]
    growth_period = dt.iloc[start_idx:start_idx + tgp].copy()

    # Initialize columns for the output DataFrame
    growth_period['STAGE_CODE'] = None
    growth_period['STAGE'] = None
    growth_period['Water Need'] = 0.0
    growth_period['Rainfall effectiveness'] = 0.0

    day_index = 0

    for stage_idx, (stage_length, kc) in enumerate(zip(stages, kc_stages), start=1):
        stage_data = growth_period.iloc[day_index:day_index + stage_length]
        water_need = (stage_data['ET0'] * kc).astype(float)
        effectiveness = (stage_data['PRECTOTCORR'] / water_need).fillna(0).astype(float) * 100

        if stage_idx == 1:
            stage = "Initial Phase"
        elif stage_idx == 2:
            stage = "Crop Development Phase"
        elif stage_idx == 3:
            stage = "Middle Season Stage"
        else:
            stage = "Late Season Stage"

        # Update the DataFrame
        growth_period.loc[stage_data.index, 'STAGE_CODE'] = stage_idx
        growth_period.loc[stage_data.index, 'STAGE'] = f"{stage}"
        growth_period.loc[stage_data.index, 'Water Need'] = water_need.values
        growth_period.loc[stage_data.index, 'Rainfall effectiveness'] = effectiveness.values

        day_index += stage_length

    growth_period.rename(columns={'PRECTOTCORR': "Rainfall"}, inplace=True)

    return growth_period#.reset_index(drop=True)


def getWaterNeeds(df: pd.DataFrame):
    dfC = df.copy()
    dfC['ds'] = pd.to_datetime(dfC['ds'])
    today = pd.Timestamp('today').normalize()
    waterNeedToday = dfC.loc[dfC['ds'] == today, 'Water Need']
    
    if not waterNeedToday.empty:
        return round(waterNeedToday.iloc[0], 2)
    else:
        return None
    

def getCurrentStage(df: pd.DataFrame):
    dfC = df.copy()
    dfC['ds'] = pd.to_datetime(dfC['ds'])
    today = pd.Timestamp('today').normalize()
    currentStage = dfC.loc[dfC['ds'] == today, 'STAGE']
    
    if not currentStage.empty:
        return currentStage.iloc[0]
    else:
        return None



def getExpectedRainfall(df: pd.DataFrame):
    dfC = df.copy()
    dfC['ds'] = pd.to_datetime(dfC['ds'])
    today = pd.Timestamp('today').normalize()
    expectedRainfall = dfC.loc[dfC['ds'] == today, 'Rainfall']
    
    if not expectedRainfall.empty:
        return round(expectedRainfall.iloc[0], 2)
    else:
        return None





def getPlot(df: pd.DataFrame, variables: list):
    """
    Generates a Bokeh plot with data from the DataFrame, including dashed lines
    to mark the end of crop development phases as specified in the STAGE column.

    :param df: pandas DataFrame containing the data
    :param variables: List of column names to be plotted
    :return: script, div tuple for embedding the plot in a Flask app
    """
    # Ensure STAGE and ds columns are present in the DataFrame
    dfC = df.copy()
    if "STAGE" not in dfC.columns:
        raise ValueError("The DataFrame must contain a 'STAGE' column.")
    if "ds" not in dfC.columns:
        raise ValueError("The DataFrame must contain a 'ds' column.")

    # Ensure ds is a datetime object and set it as the index
    dfC["ds"] = pd.to_datetime(dfC["ds"])
    dfC.set_index("ds", inplace=True)

    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(dfC.reset_index())

    # Initialize the figure
    p = figure(
        title="Crop Development Analysis",
        y_axis_label="Values (mm/day)",
        x_axis_type="datetime",
        # width=800,
        height=300,
        sizing_mode='stretch_both'
    )

    # Assign colors to variables
    colors = Spectral11[:len(variables)]

    # Plot each variable
    for color, var in zip(colors, variables):
        p.line(
            x="ds",
            y=var,
            source=source,
            line_width=2,
            color=color,
            legend_label=var
        )

    # Add dashed lines for STAGE transitions
    stages = dfC["STAGE"].dropna().unique()
    stages.sort()
    for stage in stages:  # Skip the last stage, as it doesn't have an "end"
        end_index = dfC[dfC["STAGE"] == stage].index[-1]
        dashed_line = Span(
            location=end_index.timestamp() * 1000,  # Convert datetime to milliseconds
            dimension="height",
            line_color="#d62e2e",
            line_dash="dashed",
            line_width=2
        )
        p.add_layout(dashed_line)

    # Configure legend
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.legend.background_fill_color = None
    p.legend.border_line_color = None
    p.legend.label_text_color = "white"
    p.legend.label_text_font_size = "12pt"
    p.legend.label_text_font_style = "normal"
    p.legend.spacing = 5
    p.legend.margin = 10
    p.legend.padding = 5
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    p.background_fill_color = None
    p.border_fill_color = None
    p.outline_line_color = None

    # Set white grid and axis lines
    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = None #"#dbd7d7"
    p.xaxis.axis_line_color = "white"
    p.yaxis.axis_line_color = "white"
    p.xaxis.major_tick_line_color = "white"
    p.yaxis.major_tick_line_color = "white"
    p.xaxis.minor_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    p.xaxis.axis_line_width = 2
    p.yaxis.axis_line_width = 2
    p.xaxis.major_label_text_color = "#dee5e8"
    p.yaxis.major_label_text_color = "#dee5e8"
    p.yaxis.axis_label_text_color = "#dee5e8"
    p.yaxis.axis_label_text_font_style = "normal"

    # Set title styling
    p.title.text_color = "white"
    p.title.text_font_size = "16pt"

    # Return script and div for embedding in Flask
    script, div = components(p)
    return script, div








    








