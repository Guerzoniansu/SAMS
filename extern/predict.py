import requests # For HTTP Requests on Power larc NASA
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
import xgboost as xgb
import joblib
import lightgbm as lgb


from extern import fetch as f


param_f = [
    "ALLSKY_KT",
    "ALLSKY_SRF_ALB",
    "ALLSKY_SFC_LW_DWN",
    "ALLSKY_SFC_LW_UP",
    "ALLSKY_SFC_PAR_TOT",
    "ALLSKY_SFC_SW_DWN",
    "ALLSKY_SFC_SW_UP",
    "ALLSKY_SFC_UV_INDEX",
    "ALLSKY_SFC_UVA",
    "ALLSKY_SFC_UVB",
    "CLRSKY_DAYS",
    "CLRSKY_SRF_ALB",
    "CLRSKY_SFC_LW_DWN",
    "CLRSKY_SFC_LW_UP",
    "CLRSKY_SFC_PAR_TOT",
    "CLRSKY_SFC_SW_DWN",
    "CLRSKY_SFC_SW_UP",
    "CLOUD_AMT",
    "CLOUD_AMT_DAY",
    "CLOUD_AMT_NIGHT"
]

param_f = ','.join(param_f[:])

param_s = [
    "TS",
    "U2M",
    "EVLAND",
    "EVPTRNS",
    "V2M",
    "PW",
    "PRECTOTCORR",
    "GWETPROF",
    "RH2M",
    "GWETROOT",
    "QV2M",
    "RHOA",
    "PS",
    "Z0M",
    "GWETTOP",
    "T2M",
    "WD2M",
    "WS2M"
]

param_s = ','.join(param_s[:])


glob = f.db['global']


start = "19950101"
end = date.today().strftime("%Y%m%d")
url = 'https://power.larc.nasa.gov/api/temporal/daily/point?parameters={}&community=AG&longitude={}&latitude={}&start={}&end={}&format=JSON&header=false'

def getNasaPowerData(lat: float, lon: float):
    data = glob.find_one({"lat": lat, "lon": lon, "date": date.today().year})
    if data:
        f = data["data_f"]
        s = data["data_s"]
    else:
        f = requests.get(url.format(param_f, lon, lat, start, end)) 
        f = f.json()
        # if "properties" in f and "parameter" in f["properties"]:
        #         f = f["properties"]["parameter"]
        # else:
        #     raise KeyError(f"Missing 'properties' or 'parameter' in response for parameters {param_f}: {f}")
        s = requests.get(url.format(param_s, lon, lat, start, end))
        s = s.json()

        data = {
            "lat": lat,
            "lon": lon,
            "date": date.today().year,
            "data_f": f,
            "data_s": s
        }
        glob.insert_one(data)

    f = f["properties"]["parameter"]
    s = s["properties"]["parameter"]
    dates = pd.date_range(start=start, end=end, freq='D')
    df = pd.DataFrame(index=dates)
    for param, values in f.items():
        param_data = pd.Series(values)
        param_data.index = pd.to_datetime(param_data.index, format='%Y%m%d')
        df[param] = param_data
    for param, values in s.items():
        param_data = pd.Series(values)
        param_data.index = pd.to_datetime(param_data.index, format='%Y%m%d')
        df[param] = param_data

    df.replace(-999, np.nan, inplace=True)
    return df

def getMonthlyData(lat: float, lon: float):
    dt = getNasaPowerData(lat, lon)
    end = f"{dt.index[-1].year - 1}1231"
    dt = dt.loc[:end].dropna()
    dt['month'] = dt.index.month
    dtg = dt.groupby("month").mean().reset_index()
    dtg["lat"] = lat
    dtg["lon"] = lon
    dtg = dtg.pivot(index=['lon', 'lat'], columns='month')
    dtg.columns = [f"{var}{int(time) - 1}" for var, time in dtg.columns]
    dtg.reset_index(inplace=True)
    return dtg


def predict(dt: pd.DataFrame, tech: str = "A", crop: str = "whea"):
    path = os.path.join(os.getcwd(), "datasets", "ACP", tech)
    proj_path = os.path.join(path, f"dim_projection_{tech}.csv")
    acp_coefficients = pd.read_csv(proj_path, sep=";", index_col=0)
    dtI = dt.copy()

    # columns_clrsky = [col for col in dtI.columns if col.startswith("CLRSKY_DAYS")]
    # for col in columns_clrsky:
    #     dtI[col] = dtI[col].str.extract(r'(\d+)').astype(float)

    point_test_var = dtI.drop(columns=["lon", "lat"], errors="ignore")
    point_test_var = point_test_var.drop(columns=[col for col in point_test_var.columns if f"_{tech.lower()}" in col], errors="ignore")
    point_test_var = point_test_var.drop(columns=[col for col in point_test_var.columns if "PRECTOTCORR" in col])
    point_vector = point_test_var[acp_coefficients.index]
    point_vector = np.array(point_vector)
    acp_coefficients_1 = np.array(acp_coefficients.values)
    point_reduced = np.dot(point_vector, acp_coefficients_1)
    point_reduced_vector = point_reduced.flatten()
    point_reduced_df = pd.DataFrame([point_reduced_vector], columns=acp_coefficients.columns)
    selected_columns = [col for col in dtI.columns if 'PRECTOTCORR' in col]
    sum_values = dtI[selected_columns].sum(axis=1)/12
    point_reduced_df['lon'] = (dtI['lon'].tolist())[0]
    point_reduced_df['lat'] = (dtI['lat'].tolist())[0]
    point_reduced_df['mean_PRECTOTCORR'] = (sum_values.tolist())[0]
    point_reduced_df = point_reduced_df[['lon', 'lat'] + [col for col in point_reduced_df.columns if col not in ['lon', 'lat']]]
    point_reduced_df['lon'] = pd.to_numeric(point_reduced_df['lon'], errors='coerce')
    point_reduced_df['lat'] = pd.to_numeric(point_reduced_df['lat'], errors='coerce')

    # scaler = joblib.load(os.path.join(path, f"scaler_{crop}_{tech}.pkl"))
    # point_reduced_df = scaler.transform(point_reduced_df.to_numpy())

    # means = mstd[f'mean_{crop}']
    # stds = mstd[f'std_{crop}']
    # numeric_columns = [col for col in point_reduced_df.columns if col in means.index]

    # # Standardize the values
    # standardized_values = (point_reduced_df[numeric_columns] - means[numeric_columns]) / stds[numeric_columns]
    
    # # Add the standardized values back to the DataFrame
    # for col in standardized_values.columns:
    #     point_reduced_df[col] = (standardized_values[col].tolist())[0]

    model = xgb.Booster()
    model.load_model(os.path.join(path, f"{crop}_{tech}.json"))
    data_input = xgb.DMatrix(point_reduced_df)
    prediction = model.predict(data_input)
    return round(prediction[0], 2)
    
    # try:
    #     model = xgb.Booster()
    #     model.load_model(os.path.join(path, f"{crop}_{tech}.json"))
    #     data_input = xgb.DMatrix(point_reduced_df)
    #     prediction = model.predict(data_input)
    #     return round(prediction[0], 2)
    # except:
    #     model = lgb.Booster(model_file=os.path.join(path, f"{crop}_{tech}.json"))
    #     prediction = model.predict(point_reduced_df.to_numpy(), predict_disable_shape_check=True)
    #     return round(prediction[0], 2)










