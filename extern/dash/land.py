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















