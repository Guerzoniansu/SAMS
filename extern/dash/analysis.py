# analysis.py

# manages all the external resource information that will be displayed to the user in the analysis tab
# Goes for all the levels (point, country, world)


import os
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import math
from prophet import Prophet
import calendar

from extern import fetch as f
from extern.dash.dt import dtmaker as dtm
from extern.dash import cste

todayDate = date.today()
todayDate = todayDate.strftime("%b %d, %Y")

# def getLastYear(key: str):
#     dt = dtm.transform(key)
#     return dt.index[-1].year

def getLastDate(key: str):
    dt = dtm.transform(key)
    return dt.index[-1]


def getNextYearStart(key: str):
    dt = dtm.transform(key)
    start = f"{dt.index[-1].year + 1}-01-01"
    return start

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
        'labels': list(dt.index.strftime('%Y-%m-%d')),
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


def getParamCampaignForecast(key: str, param: str, campaign: str):
    dt = dtm.transform(key)[[param.upper()]].dropna(subset=[param.upper()])
    dt['ds'] = dt.index
    dt.rename(columns={param.upper(): 'y'}, inplace=True)
    
    ld = pd.to_datetime(dt['ds'].max()) # last date in dt
    if campaign == "ny":
        eny = f"{getLastDate(key).year + 1}1231" # next year end date
        futures = pd.date_range(start=ld + pd.Timedelta(days=1), end=eny, freq='D')
        futures = pd.DataFrame({'ds': futures})
    else:
        eny = f"{getLastDate(key).year}1231" # next year end date
        futures = pd.date_range(start=ld + pd.Timedelta(days=1), end=eny, freq='D')
        futures = pd.DataFrame({'ds': futures})

    model = Prophet(growth="flat", seasonality_mode = 'additive')
    model.fit(dt)

    fcst = model.predict(futures)
    fcst = fcst[["ds", "yhat"]]
    fcst = fcst[fcst['ds'] > dt['ds'].max()]
    fcst.rename(columns={'yhat': param.upper()}, inplace=True)
    return fcst
    



def getRadParamCampaignForecast(key: str, param: str, campaign: str):
    dt = dtm.transformRadiationData(key)[[param.upper()]]
    dt['ds'] = dt.index
    dt.rename(columns={param.upper(): 'y'}, inplace=True)
    
    ld = pd.to_datetime(dt['ds'].max()) # last date in dt
    if campaign == "ny":
        eny = f"{getLastDate(key).year + 1}1231" # next year end date
        futures = pd.date_range(start=ld + pd.Timedelta(days=1), end=eny, freq='D')
        futures = pd.DataFrame({'ds': futures})
    else:
        eny = f"{getLastDate(key).year}1231" # next year end date
        futures = pd.date_range(start=ld + pd.Timedelta(days=1), end=eny, freq='D')
        futures = pd.DataFrame({'ds': futures})

    model = Prophet(growth="flat", seasonality_mode = 'additive')
    model.fit(dt)

    fcst = model.predict(futures)
    fcst = fcst[["ds", "yhat"]]
    fcst = fcst[fcst['ds'] > dt['ds'].max()]
    fcst.rename(columns={'yhat': param.upper()}, inplace=True)
    return fcst


def getCropTotalGrowthPeriod(crop: str, type: str = 'min'):
    if type == 'min':
        return cste.crop_data[crop]['mintgp']
    else:
        return cste.crop_data[crop]['maxtgp']


def calculate_best_planting_date(dt, crop: str):
    """
    Calculate the best planting date for a crop by evaluating the balance 
    between water needs and precipitation.

    Parameters:
        dt (DataFrame): DataFrame with columns ['ds', 'prectotcorr', 'et0'].
        crop (str): The crop key.

    Returns:
        str: The best planting date.
    """
    crop_info = cste.crop_data[crop]
    if type == "min":
        total_growth_period = crop_info['mintgp']
        gs = crop_info.get('gsmin', [])
    else:
        total_growth_period = crop_info['maxtgp']
        gs = crop_info.get('gsmax', [])
    kc_stages = crop_info['kc']

    best_date = None
    min_water_deficit = float('inf')

    for i in range(len(dt) - total_growth_period):
        # Define the growth period
        start_date = dt.iloc[i]['ds']
        end_date = dt.iloc[i + total_growth_period - 1]['ds']
        growth_period = dt.iloc[i:i + total_growth_period]

        # Divide growth period into stages
        if gs:
            stages = gs

        water_need = 0
        cum_precipitation = growth_period['PRECTOTCORR'].sum()
        day_index = 0

        for stage_length, kc in zip(stages, kc_stages):
            stage_data = growth_period.iloc[day_index:day_index + stage_length]
            water_need += (stage_data['ET0'] * kc).sum()
            day_index += stage_length

        # Compare water needs with precipitation
        water_deficit = abs(water_need - cum_precipitation)

        if water_deficit < min_water_deficit:
            min_water_deficit = water_deficit
            best_date = start_date

    return best_date

# def calculate_best_planting_date(dt, crop: str):
#     crop_info = cste.crop_data[crop]
#     growth_stages = len(crop_info['kc'])
#     total_growth_period = crop_info['mintgp']

#     # Calculate crop water needs
#     crop_needs = []
#     for stage in range(growth_stages):
#         days = crop_info['gsmin'][stage]
#         kc = crop_info['kc'][stage]
#         etc = dt['ET0'].rolling(window=days).sum() * kc
#         crop_needs.append(etc)

#     total_crop_water_need = sum(crop_needs)

#     # Calculate cumulative precipitation for potential planting dates
#     dt['cum_precip'] = dt['PRECTOTCORR'].rolling(window=total_growth_period).sum()

#     # Calculate deficits/surpluses
#     dt['water_deficit'] = dt['cum_precip'] - total_crop_water_need

#     # Find the best planting date (minimize deficit or surplus)
#     best_date = dt.loc[dt['water_deficit'].abs().idxmin(), 'ds']

#     return best_date, dt[['ds', 'water_deficit']]

def getForecastsTableForPlantingDate(key: str = "data", key_rad = "data_rad"):
    fcstPrectotcorr = getParamCampaignForecast(key, "prectotcorr", campaign="ny")
    fcstEt0 = getRadParamCampaignForecast(key_rad, param="et0", campaign="ny")
    sny = pd.to_datetime(f"{getLastDate(key).year + 1}0101")
    fcstPrectotcorr = fcstPrectotcorr[fcstPrectotcorr['ds'] >= sny]
    fcstEt0 = fcstEt0[fcstEt0['ds'] >= sny]
    dt = pd.merge(fcstPrectotcorr, fcstEt0, on='ds', how='inner')
    return dt

def getForecastedDataForPlot(dt: pd.DataFrame):
    dtS = dt.copy()
    dtS['ds'] = pd.to_datetime(dtS['ds']).dtS.strftime('%Y-%m-%d')
    dtS.set_index('ds', inplace=True)
    dtS.index = pd.to_datetime(dtS.index)
    dtS["month"] = dtS.index.month
    prec = ((dtS.groupby("month")["PRECTOTCORR"].sum())).tolist()
    et = ((dtS.groupby("month")["ET0"].sum())).tolist()
    return prec, et


import pandas as pd

def createCropDevelopmentDataFrame(dt: pd.DataFrame, start_date: str, crop: str, tgp: str = "max"):
    """
    Create a DataFrame for the crop development period, starting from a given date.

    Parameters:
        dt (DataFrame): DataFrame with columns ['ds', 'PRECTOTCORR', 'ET0'].
        start_date (str): The starting date in 'YYYY-MM-DD' format.
        crop (str): The crop key.
        tgp (str): Total growth period.

    Returns:
        DataFrame: A DataFrame containing crop development details.
    """
    crop_info = cste.crop_data[crop]
    if tgp == "min":
        stages = crop_info.get('gsmin', [])
    else:
        stages = crop_info.get('gsmax', [])
    kc_stages = crop_info['kc']
    total_growth_period = sum(stages)

    # Filter data starting from the given start_date
    start_idx = dt[dt['ds'] == start_date].index[0]
    growth_period = dt.iloc[start_idx:start_idx + total_growth_period].copy()

    # Initialize columns for the output DataFrame
    growth_period['STAGE_CODE'] = None
    growth_period['STAGE'] = None
    growth_period['WATER_NEED'] = 0.0
    growth_period['RAINFALL_EFFECTIVENESS'] = 0.0

    day_index = 0

    for stage_idx, (stage_length, kc) in enumerate(zip(stages, kc_stages), start=1):
        stage_data = growth_period.iloc[day_index:day_index + stage_length]
        water_need = (stage_data['ET0'] * kc).astype(float)
        effectiveness = (stage_data['PRECTOTCORR'] / water_need).fillna(0).astype(float) * 100

        if stage_idx == 1:
            stage = "ip"
        elif stage_idx == 2:
            stage = "cdp"
        elif stage_idx == 3:
            stage = "mss"
        else:
            stage = "lss"

        # Update the DataFrame
        growth_period.loc[stage_data.index, 'STAGE_CODE'] = stage_idx
        growth_period.loc[stage_data.index, 'STAGE'] = f"{stage}"
        growth_period.loc[stage_data.index, 'WATER_NEED'] = water_need.values
        growth_period.loc[stage_data.index, 'RAINFALL_EFFECTIVENESS'] = effectiveness.values

        day_index += stage_length

    return growth_period.reset_index(drop=True)


def getStageStartAndEndDate(dt: pd.DataFrame, stage: str):
    dtS = dt[dt['STAGE'] == stage]
    dtS.set_index('ds', inplace=True)
    return f"{dtS.index[0].strftime('%Y-%m-%d')} to {dtS.index[-1].strftime('%Y-%m-%d')}"


def getParamByStage(dt: pd.DataFrame, param: str):
    dtS = dt.sort_values("STAGE_CODE", ascending=True).reset_index(drop=True)
    out = (dtS.groupby("STAGE", sort=False)[param.upper()].sum()).tolist()
    return out

def getParamByMonth(dt: pd.DataFrame, param: str):
    dtS = dt.copy()
    dtS.set_index('ds', inplace=True)
    dtS.index = pd.to_datetime(dtS.index, errors='coerce')
    dtS["month"] = dtS.index.month
    out = dtS.groupby("month")[param.upper()].sum()
    out_f = [calendar.month_abbr[month] for month in out.index]
    info = {
        'labels': out_f,  # Only for labels (optional)
        'values': out.tolist()
    }
    return info


def getEffectivenessOfRainfall(wn: list, prec: list):
    wn_sum = sum(wn)
    prec_sum = sum(prec)
    return round(100 * prec_sum/wn_sum, 2)

# def getPrecipitationByStage(dt: pd.DataFrame):
#     prec = ((dt.groupby("stage")["PRECTOTCORR"].sum())).tolist()
#     return prec

# def getPrecipitationByMonth(dt: pd.DataFrame):
#     dt['ds'] = pd.to_datetime(dt['ds']).dt.strftime('%Y-%m-%d')
#     dt.set_index('ds', inplace=True)
#     dt.index = pd.to_datetime(dt.index)
#     dt["month"] = dt.index.month
#     prec = ((dt.groupby("month")["PRECTOTCORR"].sum())).tolist()
#     return prec

# def getWaterNeedByStage(dt: pd.DataFrame):
#     prec = ((dt.groupby("stage")["water_need"].sum())).tolist()
#     return prec

# def getWaterNeedByMonth(dt: pd.DataFrame):
#     dt['ds'] = pd.to_datetime(dt['ds']).dt.strftime('%Y-%m-%d')
#     dt.set_index('ds', inplace=True)
#     dt.index = pd.to_datetime(dt.index)
#     dt["month"] = dt.index.month
#     prec = ((dt.groupby("month")["water_need"].sum())).tolist()
#     return prec



def getCropOptimalPlantingDate(dt, crop: str, type: str = 'min', key: str = "data", key_rad = "data_rad"):
    best_date = calculate_best_planting_date(dt=dt, crop=crop)
    return best_date.strftime("%b %d, %Y")

    


