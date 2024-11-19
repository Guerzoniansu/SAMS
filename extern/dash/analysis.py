# analysis.py

# manages all the external resource information that will be displayed to the user in the analysis tab
# Goes for all the levels (point, country, world)


import os
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import math

from extern import fetch as f
from extern.dash.dt import dtmaker as dtm
from extern.dash import cste as c

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


def getMeanAnnualParam(key: str, param: str = "prectotcorr"):
    start = "19950101"
    dt = dtm.transform(key)[[param.upper()]]
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[start:end].dropna(subset=[param.upper()])
    dt = dt.resample("Y").sum()
    return round(dt.mean().iloc[0], 2)


def getMonthlyParamDataMean(key: str, param: str = "t2m"):
    dt = dtm.transform(key)[[param.upper()]]
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[:end].dropna(subset=[param.upper()])
    dt["month"] = dt.index.month
    vals = ((dt.groupby("month")[param.upper()].mean())).tolist()
    return vals


def getMonthlyParamDataSum(key: str, param: str = "prectotcorr"):
    dt = dtm.transform(key)[[param.upper()]]
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[:end].dropna(subset=[param.upper()])
    nbYear = dt.index.year.nunique()
    dt["month"] = dt.index.month
    vals = ((dt.groupby("month")[param.upper()].sum())/nbYear).tolist()
    return vals

# def getMonthlyPrecipitationData(key: str, param: str = "prectotcorr"):
#     dt = dtm.transform(key)[[param.upper()]]
#     end = f"{dt.index[-1].year - 1}1231"
#     dt = dt.loc[:end].dropna(subset=[param.upper()])
#     nbYear = dt.index.year.nunique()
#     dt["month"] = dt.index.month
#     vals = ((dt.groupby("month")[param.upper()].sum())/nbYear).tolist()
#     return vals


def getPrecipitationSuitabilityAgriculture(key: str, param: str = "prectotcorr"):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    p = getMeanAnnualParam(key, param)
    if p<0 or p>1200:
        return 0
    else:
        return round((1/3600)*p*(1200-p), 2)


# def getMonthlyTemperatureData(key: str, param: str = "t2m"):
#     dt = dtm.transform(key)[[param.upper()]]
#     end = f"{dt.index[-1].year - 1}1231"
#     dt = dt.loc[:end].dropna(subset=[param.upper()])
#     dt["month"] = dt.index.month
#     vals = ((dt.groupby("month")[param.upper()].mean())).tolist()
#     return vals

def getPrecipitationEffectivenessIndex(key: str):
    monthPrecipitation = getMonthlyParamDataSum(key)
    monthPrecipitation = [p * 0.0393701 for p in monthPrecipitation]
    monthTemperature = getMonthlyParamDataMean(key, param="t2m")
    monthTemperature = [t * 9/5 + 32 for t in monthTemperature]

    peiMonth = [115 * ((p/(t - 10))**(10/9)) for p, t in zip(monthPrecipitation, monthTemperature)]
    return round(sum(peiMonth), 2)

def getClimateTypeFromPei(pei):
    if pei < 16:
        return "Arid"
    elif pei >= 16 and pei <= 31:
        return "Semi-arid"
    elif pei >= 32 and pei <= 63:
        return "Sub-humid"
    elif pei >= 64 and pei <= 127:
        return "Humid"
    else:
        return "Wet"

# def getCropFactorsTable():
#     dt = pd.DataFrame.from_dict(c.crop_data, orient='index')
#     dt['kcis'] = dt['kc'].apply(lambda x: x[0])
#     dt['kcds'] = dt['kc'].apply(lambda x: x[1])
#     dt['kcmss'] = dt['kc'].apply(lambda x: x[2])
#     dt['kclss'] = dt['kc'].apply(lambda x: x[3])
#     dt.drop(columns=['kc'], inplace=True)
#     dt['crop'] = dt.index
#     dt = dt[['crop', 'mintgp', 'maxtgp', 'kcis', 'kcds', 'kcmss', 'kclss']]
#     html = dt.to_html(index=False, escape=False)
#     return html


def getMeanHistorySoilParams(key: str):
    dt = dtm.transform(key)[["GWETPROF", "GWETROOT", "GWETTOP"]]
    return np.round(dt.mean().values, 2)

def getSoilParamAgriSuitability(key: str):
    vals = getMeanHistorySoilParams(key)
    for i, val in enumerate(vals):
        if val <= 0.3 or val >= 0.7:
            vals[i] = 0
        else:
            vals[i] = round(-2500*(val-0.3)*(val-0.7), 2)
    return vals

# def getHistoryET0Data(key: str, param: str = "et0"):
#     dt = dtm.transformRadiationData(key)[[param.upper()]]
#     info = {
#         'labels': list(dt.index.strftime('%Y-%m-%d')),  # Only for labels (optional)
#         'values': list(dt[param.upper()])
#     }
#     return info
    


def getRadMonthlyParamDataSum(key: str, param: str = "et0"):
    dt = dtm.transformRadiationData(key)[[param.upper()]]
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[:end].dropna(subset=[param.upper()])
    nbYear = dt.index.year.nunique()
    dt["month"] = dt.index.month
    vals = ((dt.groupby("month")[param.upper()].sum())/nbYear).tolist()
    return vals

def getRadMonthlyParamDataMean(key: str, param: str = "rh2m"):
    dt = dtm.transformRadiationData(key)[[param.upper()]]
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[:end].dropna(subset=[param.upper()])
    dt["month"] = dt.index.month
    vals = ((dt.groupby("month")[param.upper()].mean())).tolist()
    return vals


# def getMonthlyParamData(key: str, param: str = "rh2m"):
#     dt = dtm.transform(key)[[param.upper()]]
#     end = f"{dt.index[-1].year - 1}1231"
#     dt = dt.loc[:end].dropna(subset=[param.upper()])
#     dt["month"] = dt.index.month
#     vals = ((dt.groupby("month")[param.upper()].mean())).tolist()
#     return vals



    


