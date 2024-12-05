import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import os
import math

from extern import fetch as f

start = "19950101"
end = date.today() - timedelta(days=2)
end = end.strftime("%Y%m%d")

def getData(key: str):
    return f.dtDict[key]

def transform(key: str):
    dates = pd.date_range(start=start, end=end, freq='D')
    df = pd.DataFrame(index=dates)
    params = getData(key)["data"]["properties"]["parameter"]
    for param, values in params.items():
        param_data = pd.Series(values)
        param_data.index = pd.to_datetime(param_data.index, format='%Y%m%d')
        df[param] = param_data

    df.replace(-999, np.nan, inplace=True)
    # if not os.path.exists("E:/SAMS/datasets/clim.xlsx"):
    #     df.to_excel("E:/SAMS/datasets/clim.xlsx", index=True)
    
    return df

def getLastNDays(key: str, n: int = 30, dec: int = 0):
    df = transform(key)
    return df.iloc[-7-int(n)-dec:-7]

def getCountryData(lat: float, lon: float, var: str, tech: str, year: str, type: str = "country"):
    return f.getCountryData(lat, lon, var, tech, year)

# def getCountryRasterDataFromPoint(lat: float, lon: float, var: str, tech: str, year: str, crops: str):
#     return f.runFetcher(lat, lon, var, tech, year, crops)


def e(t):
    return 0.6108 * math.exp((17.27 * t)/(t + 237.3))

# a = 0.23 for grass (reference)
def calcEvptrnsRef(tmin, tmax, rs, u2, z, rh2, date, lat, a: int = 0.23, gsc: float = 0.0820):
    """
        Args:
            tmin: minimum daily air temperature, ºC
            tmax:  maximum daily air temperature, ºC
            rs: Mean daily solar radiation MJm-2day-1
            u2: Wind speed at 2 meters
            z: altitude
            rh2: Relative humidity at 2 meters
            date: today
            lat: latitude
            a:  albedo or canopy reflection coefficient, which is 0.23 for the hypothetical grass reference crop, dimensionless
            gsc:  solar constant = 0.0820 MJ m-2 min-1
        returns:
            Evapotranspiration ET0
    """
    tmean = (tmin + tmax)/2 # mean daily air temperature, ºC
    delta = (4098 * (e(tmean)))/((tmean + 273.3) ** 2) # Slope of saturation vapor pressure curve
    p = 101.3 * (((293 - 0.0065 * z)/293) ** 5.26) # Atmospheric Pressure
    gamma = 0.000665 * p # Psychrometric constant
    dt = delta/(delta + gamma * (1 + 0.34 * u2)) # Delta Term
    pt = gamma/(delta + gamma * (1 + 0.34 * u2)) # Psi Term
    tt = u2 * (900/(tmean + 273)) # Temperature Term
    es = (e(tmin) + e(tmax))/2 # Mean saturation vapor pressure derived from air temperature
    ea = es * (rh2/100) # Actual vapor pressure derived from relative humidity
    j = (datetime.strptime(date, "%d/%m/%Y") - datetime(datetime.strptime(date, "%d/%m/%Y").year, 1, 1)).days
    dr = 1 + 0.033 * math.cos(2 * math.pi * j/365) # inverse relative distance Earth-Sun 
    sigma = 0.409 * math.sin(2 * math.pi * j/365 - 1.39) # solar declination
    rho = math.pi * lat/180
    ws = math.acos(-math.tan(rho) * math.tan(sigma)) # Sunset hour angle
    ra = (24 * 60/math.pi) * gsc * dr * (ws * math.sin(rho) * math.sin(sigma) + math.cos(rho) * math.cos(sigma) * math.sin(ws)) # Extraterrestrial radiation MJ m-2 day-1
    rso = (0.75 + 2 * (10 ** (-5)) * z) * ra
    rns = (1 - a) * rs # Net solar or net shortwave radiation
    rnl = 4.903 * (10 ** (-9)) * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4)/2) * (0.34 - 0.14 * (ea ** (1/2))) * (1.35 * (rs/rso) - 0.35)
    rn = rns - rnl
    rng = 0.408 * rn
    et_rad = dt * rng
    et_wind = pt * tt * (es - ea)
    return et_rad + et_wind


def transformRadiationData(key: str):
    """
    Creates a new column 'ET0' in the DataFrame, calculating Evapotranspiration reference for each row.
    Args:
        key: The name of the DataFrame key to be transformed.
    """
    dt = transform(key)
    def calc(row):
        return calcEvptrnsRef(
            tmin=row["T2M_MIN"],
            tmax=row["T2M_MAX"],
            rs=row["ALLSKY_SFC_SW_DWN"],
            u2=row["WS2M"],
            z=f.coords[2],
            rh2=row["RH2M"],
            date=row.name.strftime("%d/%m/%Y"),
            lat=float(f.coords[0])
        )
    dt["ET0"] = dt.apply(calc, axis=1)
    dt.replace(-999, np.nan, inplace=True)
    # if not os.path.exists("E:/SAMS/datasets/rad.xlsx"):
    #     dt.to_excel("E:/SAMS/datasets/rad.xlsx", index=True)
    return dt

