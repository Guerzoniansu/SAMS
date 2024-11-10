# analysis.py

# manages all the external resource information that will be displayed to the user in the analysis tab
# Goes for all the levels (point, country, world)


import os
import pandas as pd
import numpy as np
from datetime import date, timedelta

from extern import fetch as f
from extern.dash.dt import dtmaker as dtm

todayDate = date.today()
todayDate = todayDate.strftime("%b %d, %Y")

def getCountryCode(lat: str, lon: str, year: str = "2010"):
    code: list = f.getCountryFromPoint(lat, lon, year)
    if isinstance(code, list):
        return code[0]
    return code

def getParamLastUpdate(param: str, key: str):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    return dt.index[-1].strftime("%b %d, %Y")

def getParamLastValue(param: str, key: str):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    return round(dt.iloc[-1].values[0], 2)

def getParamGrowthRate(param: str, key: str):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    rate = round(100 * (dt.iloc[-1].values[0] - dt.iloc[-2].values[0])/dt.iloc[-2].values[0], 2)
    if rate > 0:
        state = "sup"
    elif rate < 0:
        state = "inf"
    else:
        state = "equ"
    return f"{rate:+.2f}", state

def getParamLastSevenDaysValues(param: str, key: str):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    dt = dt.iloc[-8:-1]
    info = {
        'labels': list(dt.index.strftime('%Y-%m-%d')),  # Only for labels (optional)
        'values': list(dt[param.upper()])
    }
    return info

def getParamConditionIndexValue(key: str, param: str = "t2m"):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    val = (dt[param.upper()].max() - dt[param.upper()].iloc[-1])/(dt[param.upper()].max() - dt[param.upper()].min()) # (max-current)/(max-min)
    return round(100 * val)


def getMeanAnnualPrecipitation(key: str, param: str = "prectotcorr"):
    start = "19950101"
    dt = dtm.transform(key)[[param.upper()]]
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[start:end].dropna(subset=[param.upper()])
    dt = dt.resample("Y").sum()
    return round(dt.mean().iloc[0], 2)

def getMonthlyPrecipitationData(key: str, param: str = "prectotcorr"):
    dt = dtm.transform(key)[[param.upper()]]
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[:end].dropna(subset=[param.upper()])
    nbYear = dt.index.year.nunique()
    dt["month"] = dt.index.month
    vals = ((dt.groupby("month")[param.upper()].sum())/nbYear).tolist()
    return vals




