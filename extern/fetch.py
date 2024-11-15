# fetch.py

# this file is the one responsible for fetching data on Power Larc NASA web site
# The principle is to get interesting parameters that can be analysed for future use purpose
# taking into account that the number of parameter per API call is limited to 20
# Thus, we will be collecting the data in several shots if necessary
# Be aware of the fact that we are using the Agroclimatology (AG) as default community for data requests

import requests # For HTTP Requests on Power larc NASA
import pandas as pd
from pymongo import MongoClient # MongoDB Atlas
import numpy as np
from datetime import date, timedelta
import geopandas as gpd
from shapely.geometry import Point
from io import StringIO
import os
from urllib.parse import quote_plus
import asyncio
import aiohttp
import gridfs
from io import BytesIO

param = [
    'EVLAND', # Evaporation Land: The evaporation over land at the surface of the earth
    'EVPTRNS', # Evapotranspiration Energy Flux: The evapotranspiration energy flux at the surface of the earth.
    'GWETPROF', # Profile Soil Moisture
    'WS2M', # Wind Speed at 2 Meters
    'T2M', # Temperature at 2 meters
    'TS', # Earth Skin Temperature: The average temperature at the earth's surface
    'QV2M', # Specific Humidity at 2 Meters: The ratio of the mass of water vapor to the total mass of air at 2 meters (g water/kg total air).
    'RH2M', # Relative Humidity at 2 Meters: The ratio of actual partial pressure of water vapor to the partial pressure at saturation, expressed in percent.
    'PS', # Surface Pressure
    'WD2M', # Wind Direction at 2 Meters
    'CLOUD_AMT_DAY', # Cloud Amount at Daylight
    'PW', # Precipitable Water: The total atmospheric water vapor contained in a vertical column of the atmosphere
    'T2MDEW', # The dew/frost point temperature at 2 meters above the surface of the earth
    'FROST_DAYS', # Frost Days: A frost day occurs when the 2m temperature cools to the dew point temperature and both are less than 0 C or 32 F.
    'GWETROOT', # Root Zone Soil Wetness
    'GWETTOP', # Surface Soil Wetness
    'PRECTOTCORR', # Precipitation Corrected
    'Z0M' # Surface Roughness
]

params = ','.join(param[:])

password = quote_plus("mongodbatlasBlessing16@#")
uri = f"mongodb+srv://alagbehamid:{password}@sams.9s76z.mongodb.net/?retryWrites=true&w=majority&appName=sams" # mongodb connection string
client = MongoClient(uri)
db = client['sams']
wsCol = db['wsCollection']
agCol = db['agCollection']

start = "19950101"
end = date.today() - timedelta(days=2)
end = end.strftime("%Y%m%d")
url = 'https://power.larc.nasa.gov/api/temporal/daily/point?parameters={}&community=RE&longitude={}&latitude={}&start={}&end={}&format=JSON&header=false'

dtDict: dict = {} # dict for storing climate data from power larc used in single point (lat, lon) query
coords = [None, None] # coordinates


world = gpd.read_file("ws/world-administrative-boundaries.shp", encoding="ISO-8859-1") # file to identify countries

def getPointData(lat: float, lon: float):
    """
        params:
            lat: float,
            lon: float,
        returns:
            data: dict[str, Any]
        Gets data on Power Larc NASA for the query point and returns it as dictionnary
    """
    r = requests.get(url.format(params, lon, lat, start, end))
    data = {
        "lat": lat,
        "lon": lon,
        "date": date.today().strftime("%Y%m%d"),
        "data": r.json()
    }
    wsCol.insert_one(data)
    return data

def getCachedData(lat, lon):
    """
        params:
            lat: float,
            lon: float,
        returns:
            data: dict[str, Any]
        Search for already known data for query point in MongoDB Atlas Collection
    """
    data = wsCol.find_one({"lat": lat, "lon": lon, "date": date.today().strftime("%Y%m%d")})
    return data

def getCountryFromPoint(lat: float, lon: float, year: str):
    """
        params:
            lat: float,
            lon: float,
            year: str
        returns:
            str|list[str]
        Get country name or iso3 code using world shapefile
    """
    point = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs="EPSG:4326")
    country = world[world.contains(point.iloc[0].geometry)]
    if year == "2010": # for differences in column names in databases 2010 and 2020
        return country["iso3"].iloc[0]
    else:
        return [country["i_3166_"].iloc[0], country["name"].iloc[0]]


urlS3 = "https://sams-s3.s3.us-east-1.amazonaws.com/{}" # API URL for making requests

def getKey(var: str, tech: str, year: str):
    """
        params:
            var: str,
            tech: str,
            year: str
        returns:
            str
        Returns the key to the corresponding csv file we want to load
    """
    if year == "2005":
        if var != "physicalArea":
            key = os.path.join(var, tech, f"spam{year}V3r2_global_{var[0].upper()}_T{tech}.csv")
            return key
        else:
            key = f"{var}/{tech}/spam{year}V3r2_global_A_T{tech}.csv"
            return key
    elif year == "2010":
        if var != "physicalArea":
            key = f"{var}/{tech}/spam{year}V2r0_global_{var[0].upper()}_T{tech}.csv"
            return key
        else:
            key = f"{var}/{tech}/spam{year}V2r0_global_A_T{tech}.csv"
            return key
    else:
        if var != "physicalArea":
            key = f"{var}/{tech}/spam{year}V1r0_global_{var[0].upper()}_T{tech}.csv"
            return key
        else:
            key = f"{var}/{tech}/spam{year}V1r0_global_A_T{tech}.csv"
            return key

def getKeyData(key: str):
    """
        params:
            key: str
        returns:
            str|StringIO
        return the path (for local computing) or object (for s3 computation)
    """
    lPath = os.path.join(os.getcwd(), "files", key)
    if os.path.isfile(lPath): # path exists locally
        return lPath
    else:
        obj = requests.get(urlS3.format(key))
        return StringIO(obj.text)


def getCountryData(lat: float, lon: float, var: str, tech: str, year: str, type: str = "country"):
    """
        params:
            lat: float,
            lon: float,
            var: str,
            tech: str,
            year: str,
            type: str = "country"
        returns:
            pd.Dataframe
    """
    if type == "country":
        chunks = []
        key = getKey(var, tech, year)
        for chunk in pd.read_csv(getKeyData(key), chunksize=10000, encoding="ISO-8859-1"):
            if year == "2010": # columns iso3 in 2010 mapspam dataset
                filtered = chunk[chunk["iso3"] == getCountryFromPoint(lat, lon, year)] # filter for country data only
            else:
                filtered = chunk[(chunk["FIPS0"] == getCountryFromPoint(lat, lon, year)[0]) | (chunk["ADM0_NAME"] == getCountryFromPoint(lat, lon, year)[1])]
            chunks.append(filtered)
        
        dt = pd.concat(chunks, ignore_index=True)
        return dt
    else:
        key = getKey(var, tech, year)
        return pd.read_csv(getKeyData(key), encoding="ISO-8859-1")



def getCoordsPointCountry(lat: float, lon: float, var: str, tech: str, year: str, crops: str):
    """
        params:
            lat: float,
            lon: float,
            var: str,
            tech: str,
            year: str,
            crop: str
        returns:
            pd.Dataframe
    """
    cropsT = f"{crops.lower()}_{tech.lower()}" if crops else []
    dt = getCountryData(lat, lon, var, tech, year)
    dt.columns = dt.columns.str.lower()
    dt = dt[['x', 'y', cropsT]]
    dt = dt.rename(columns={cropsT: "crop"})
    dt = dt[(dt['crop'] != 0) & (dt['crop'].notna())]
    return dt[['x', 'y']].values, dt



""" urlC = 'https://power.larc.nasa.gov/api/temporal/monthly/point?start={}&end={}&latitude={}&longitude={}&community=RE&parameters={}&format=json&header=false'
def getTasks(session, coords, year):
    tasks = []
    for coord in coords:
        tasks.append(asyncio.create_task(session.get(urlC.format(year, year, coord[1], coord[0], params), ssl=False)))
    return tasks

async def fetcher(lat: float, lon: float, var: str, tech: str, year: str, crops: str):
    eF = agCol.find_one({"filename": f"{getCountryFromPoint(lat, lon, year)}.csv"})
    if eF:
        with agCol.get(eF._id) as file:
            dt = pd.read_csv(file)
        return dt
        
    coords, crop = getCoordsPointCountry(lat, lon, var, tech, year, crops)
    if isinstance(coords, np.ndarray) and coords.size == 0:
        return None
    dt = pd.DataFrame()
    async with aiohttp.ClientSession() as s:
        tasks = getTasks(s, coords, year)
        responses = await asyncio.gather(*tasks)
        for idx, r in enumerate(responses):
            resp = {
                "lat": lat,
                "lon": lon,
                "data": await r.json()
            }
            return resp["data"]
            params = resp["data"]["properties"]["parameter"]
            coordVal = {'x': coords[idx][0], 'y': coords[idx][1]}
            for param, values in params.items():
                coordVal[param] = values[f"{year}13"]
            dt = pd.concat([dt, pd.DataFrame([coordVal])], ignore_index=True)
    dt = dt.merge(crop[['x', 'y', 'crop']], on=['x', 'y'], how='left')
    cB = BytesIO()
    dt.to_csv(cB, index=False)
    cB.seek(0)
    agCol.put(cB, filename=f"{getCountryFromPoint(lat, lon, year)}.csv")
    return dt

def runFetcher(lat: float, lon: float, var: str, tech: str, year: str, crops: str):
    return asyncio.run(fetcher(lat, lon, var, tech, year, crops)) """









