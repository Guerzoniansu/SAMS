from flask import Flask, request, render_template, redirect, url_for, jsonify
import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from datetime import date, timedelta


from extern import fetch as f
from extern.dash.clim import statClim as stc
from extern.dash.clim import plotClim as ptc
from extern.dash.soil import statSoil as sts
from extern.dash.soil import plotSoil as pts
from extern.dash.params import stat as s
from extern.dash.params import plot as p
from extern.dash import analysis as a
from extern.dash import land as l
from extern import predict

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard/home', methods=['GET','POST'])
def loadDashHome():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)

    f.coords.append(lat)
    f.coords.append(lon)
    data = f.getCachedData(lat, lon)
    radiationData = f.getRadiationCachedData(lat, lon)
    if data:
        pass
    else:
        data = f.getPointData(lat, lon)
    if radiationData:
        pass
    else:
        radiationData = f.getRadiationPointData(lat, lon)
    f.coords.append(data["data"]["geometry"]["coordinates"][2])
    f.dtDict.clear()
    f.dtDict["data"] = data
    f.dtDict["data_rad"] = radiationData
    nyStart = a.getNextYearStart(key="data")
    today = date.today()
    return render_template('dashboard/home.html',rlon = lon, rlat = lat, lon=round(float(lon), 2), lat=round(float(lat), 2), today = today, nyStart = nyStart)

@app.route(f'/dashboard/climate', methods=['GET','POST'])
def loadDashClimate():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        cOneDays = request.args.get('cOneDays', default=30)

    means, cmpMeans = stc.calcClimMeans(key=key, days=cOneDays)
    stds, cmpStds = stc.calcClimStd(key=key, days=cOneDays)
    mins, cmpMins = stc.calcClimMin(key=key, days=cOneDays)
    maxs, cmpMaxs = stc.calcClimMax(key=key, days=cOneDays)
    current, rate, cmp = stc.getLastBeforeLast(key=key)
    pESTemp = ptc.plotESTempLastNDays(key=key, days=cOneDays)
    pSHum = ptc.plotSHumLastNDays(key=key, days=cOneDays)
    pSPres = ptc.plotSPresLastNDays(key=key, days=cOneDays)
    pWDir = ptc.plotWDirLastNDays(key=key, days=cOneDays)
    scriptESTemp, divESTemp = components(pESTemp)
    scriptSHum, divSHum = components(pSHum)
    scriptSPres, divSPres = components(pSPres)
    scriptWDir, divWDir = components(pWDir)
    return render_template('dashboard/climate.html', 
                           rlon = lon, 
                           rlat = lat,
                           mEvland = means[0],
                           mEvptrns = means[1],
                           mWs2m = means[2],
                           mT2m = means[3],
                           mTs = means[4],
                           mQv2m = means[5],
                           mRh2m = means[6],
                           mPs = means[7],
                           mWd2m = means[8],
                           mCloudAmtDay = means[9],
                           mPw = means[10],
                           mT2mDew = means[11],
                           mForstDays = means[12],
                           mPrectotCorr = means[13],
                           stdEvland = stds[0],
                           stdEvptrns = stds[1],
                           stdWs2m = stds[2],
                           stdT2m = stds[3],
                           stdTs = stds[4],
                           stdQv2m = stds[5],
                           stdRh2m = stds[6],
                           stdPs = stds[7],
                           stdWd2m = stds[8],
                           stdCloudAmtDay = stds[9],
                           stdPw = stds[10],
                           stdT2mDew = stds[11],
                           stdForstDays = stds[12],
                           stdPrectotCorr = stds[13],
                           minEvland = mins[0],
                           minEvptrns = mins[1],
                           minWs2m = mins[2],
                           minT2m = mins[3],
                           minTs = mins[4],
                           minQv2m = mins[5],
                           minRh2m = mins[6],
                           minPs = mins[7],
                           minWd2m = mins[8],
                           minCloudAmtDay = mins[9],
                           minPw = mins[10],
                           minT2mDew = mins[11],
                           minForstDays = mins[12],
                           minPrectotCorr = mins[13],
                           maxEvland = maxs[0],
                           maxEvptrns = maxs[1],
                           maxWs2m = maxs[2],
                           maxT2m = maxs[3],
                           maxTs = maxs[4],
                           maxQv2m = maxs[5],
                           maxRh2m = maxs[6],
                           maxPs = maxs[7],
                           maxWd2m = maxs[8],
                           maxCloudAmtDay = maxs[9],
                           maxPw = maxs[10],
                           maxT2mDew = maxs[11],
                           maxForstDays = maxs[12],
                           maxPrectotCorr = maxs[13],

                           cmpMeanEvland = cmpMeans[0],
                           cmpMeanEvptrns = cmpMeans[1],
                           cmpMeanWs2m = cmpMeans[2],
                           cmpMeanT2m = cmpMeans[3],
                           cmpMeanTs = cmpMeans[4],
                           cmpMeanQv2m = cmpMeans[5],
                           cmpMeanRh2m = cmpMeans[6],
                           cmpMeanPs = cmpMeans[7],
                           cmpMeanWd2m = cmpMeans[8],
                           cmpMeanCloudAmtDay = cmpMeans[9],
                           cmpMeanPw = cmpMeans[10],
                           cmpMeanT2mDew = cmpMeans[11],
                           cmpMeanForstDays = cmpMeans[12],
                           cmpMeanPrectotCorr = cmpMeans[13],
                           cmpStdEvland = cmpStds[0],
                           cmpStdEvptrns = cmpStds[1],
                           cmpStdWs2m = cmpStds[2],
                           cmpStdT2m = cmpStds[3],
                           cmpStdTs = cmpStds[4],
                           cmpStdQv2m = cmpStds[5],
                           cmpStdRh2m = cmpStds[6],
                           cmpStdPs = cmpStds[7],
                           cmpStdWd2m = cmpStds[8],
                           cmpStdCloudAmtDay = cmpStds[9],
                           cmpStdPw = cmpStds[10],
                           cmpStdT2mDew = cmpStds[11],
                           cmpStdForstDays = cmpStds[12],
                           cmpStdPrectotCorr = cmpStds[13],
                           cmpMinEvland = cmpMins[0],
                           cmpMinEvptrns = cmpMins[1],
                           cmpMinWs2m = cmpMins[2],
                           cmpMinT2m = cmpMins[3],
                           cmpMinTs = cmpMins[4],
                           cmpMinQv2m = cmpMins[5],
                           cmpMinRh2m = cmpMins[6],
                           cmpMinPs = cmpMins[7],
                           cmpMinWd2m = cmpMins[8],
                           cmpMinCloudAmtDay = cmpMins[9],
                           cmpMinPw = cmpMins[10],
                           cmpMinT2mDew = cmpMins[11],
                           cmpMinForstDays = cmpMins[12],
                           cmpMinPrectotCorr = cmpMins[13],
                           cmpMaxEvland = cmpMaxs[0],
                           cmpMaxEvptrns = cmpMaxs[1],
                           cmpMaxWs2m = cmpMaxs[2],
                           cmpMaxT2m = cmpMaxs[3],
                           cmpMaxTs = cmpMaxs[4],
                           cmpMaxQv2m = cmpMaxs[5],
                           cmpMaxRh2m = cmpMaxs[6],
                           cmpMaxPs = cmpMaxs[7],
                           cmpMaxWd2m = cmpMaxs[8],
                           cmpMaxCloudAmtDay = cmpMaxs[9],
                           cmpMaxPw = cmpMaxs[10],
                           cmpMaxT2mDew = cmpMaxs[11],
                           cmpMaxForstDays = cmpMaxs[12],
                           cmpMaxPrectotCorr = cmpMaxs[13],

                           temp = current[3],
                           rHumidity = current[6],
                           precipCorr = current[13],
                           windSpeed = current[2],
                           tempRate = rate[3],
                           rHumidityRate = rate[6],
                           precipCorrRate = rate[13],
                           windSpeedRate = rate[2],
                           tempCmp = cmp[3],
                           rHumidityCmp = cmp[6],
                           precipCorrCmp = cmp[13],
                           windSpeedCmp = cmp[2],

                           scriptESTemp=scriptESTemp,
                           divESTemp=divESTemp,
                           scriptWDir=scriptWDir,
                           divWDir=divWDir,
                           scriptSPres=scriptSPres,
                           divSPres=divSPres,
                           scriptSHum=scriptSHum,
                           divSHum=divSHum
                        )


@app.route(f'/dashboard/soil', methods=['GET','POST'])
def loadDashSoil():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        cOneDays = request.args.get('cOneDays', default=30)

    means, cmpMeans = sts.calcSoilMeans(key=key, days=cOneDays)
    stds, cmpStds = sts.calcSoilStd(key=key, days=cOneDays)
    mins, cmpMins = sts.calcSoilMin(key=key, days=cOneDays)
    maxs, cmpMaxs = sts.calcSoilMax(key=key, days=cOneDays)
    current, rate, cmp = sts.getLastBeforeLast(key=key)
    pGWETPROF = pts.plotGWETPROFLastNDays(key=key, days=cOneDays)
    pGWETROOT = pts.plotGWETROOTLastNDays(key=key, days=cOneDays)
    pGWETTOP = pts.plotGWETTOPLastNDays(key=key, days=cOneDays)
    pZ0M = pts.plotZ0MLastNDays(key=key, days=cOneDays)
    scriptPSMois, divPSMois = components(pGWETPROF)
    scriptRZSW, divRZSW = components(pGWETROOT)
    scriptSSWet, divSSWet = components(pGWETTOP)
    scriptSRough, divSRough = components(pZ0M)
    return render_template('dashboard/soil.html', 
                           rlon = lon, 
                           rlat = lat,
                           mGwetprof = means[0],
                           mGwetroot = means[1],
                           mGwettop = means[2],
                           mZom = means[3],
                           stdGwetprof = stds[0],
                           stdGwetroot = stds[1],
                           stdGwettop = stds[2],
                           stdZom = stds[3],
                           minGwetprof = mins[0],
                           minGwetroot = mins[1],
                           minGwettop = mins[2],
                           minZom = mins[3],
                           maxGwetprof = maxs[0],
                           maxGwetroot = maxs[1],
                           maxGwettop = maxs[2],
                           maxZom = maxs[3],

                           cmpMeanGwetprof = cmpMeans[0],
                           cmpMeanGwetroot = cmpMeans[1],
                           cmpMeanGwettop = cmpMeans[2],
                           cmpMeanZom = cmpMeans[3],
                           cmpStdGwetprof = cmpStds[0],
                           cmpStdGwetroot = cmpStds[1],
                           cmpStdGwettop = cmpStds[2],
                           cmpStdZom = cmpStds[3],
                           
                           cmpMinGwetprof = cmpMins[0],
                           cmpMinGwetroot = cmpMins[1],
                           cmpMinGwettop = cmpMins[2],
                           cmpMinZom = cmpMins[3],
                           
                           cmpMaxGwetprof = cmpMaxs[0],
                           cmpMaxGwetroot = cmpMaxs[1],
                           cmpMaxGwettop = cmpMaxs[2],
                           cmpMaxZom = cmpMaxs[3],
                           

                           gwetprof = current[0],
                           gwetroot = current[1],
                           gwettop = current[2],
                           zom = current[3],
                           gwetprofRate = rate[0],
                           gwetrootRate = rate[1],
                           gwettopRate = rate[2],
                           zomRate = rate[3],
                           gwetprofCmp = cmp[0],
                           gwetrootCmp = cmp[1],
                           gwettopCmp = cmp[2],
                           zomCmp = cmp[3],

                           scriptPSMois=scriptPSMois,
                           divPSMois=divPSMois,
                           scriptSRough=scriptSRough,
                           divSRough=divSRough,
                           scriptSSWet=scriptSSWet,
                           divSSWet=divSSWet,
                           scriptRZSW=scriptRZSW,
                           divRZSW=divRZSW
                        )




@app.route('/dashboard/climate/evland', methods=['GET','POST'])
def loadDashClimateEvland():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="EVLAND")
    min, minDate = s.calcMin(key=key, param="EVLAND")
    max, maxDate = s.calcMax(key=key, param="EVLAND")
    std = s.calcStd(key=key, param="EVLAND")
    plot = p.plot(key=key, param="EVLAND", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="EVLAND", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="EVLAND", period=int(fcstDays))
    return render_template('dashboard/climate/evland.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           minDate = minDate,
                           maxDate = maxDate,
                           std = std[0],
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/evptrns', methods=['GET','POST'])
def loadDashClimateEvptrns():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="EVPTRNS")
    min, minDate = s.calcMin(key=key, param="EVPTRNS")
    std = s.calcStd(key=key, param="EVPTRNS")
    max, maxDate = s.calcMax(key=key, param="EVPTRNS")
    plot = p.plot(key=key, param="EVPTRNS", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="EVPTRNS", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="EVPTRNS", period=int(fcstDays))
    return render_template('dashboard/climate/evptrns.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )


@app.route('/dashboard/climate/ws2m', methods=['GET','POST'])
def loadDashClimateWs2m():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="WS2M")
    min, minDate = s.calcMin(key=key, param="WS2M")
    std = s.calcStd(key=key, param="WS2M")
    max, maxDate = s.calcMax(key=key, param="WS2M")
    plot = p.plot(key=key, param="WS2M", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="WS2M", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="WS2M", period=int(fcstDays))
    return render_template('dashboard/climate/ws2m.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/t2m', methods=['GET','POST'])
def loadDashClimateT2m():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="T2M")
    min, minDate = s.calcMin(key=key, param="T2M")
    std = s.calcStd(key=key, param="T2M")
    max, maxDate = s.calcMax(key=key, param="T2M")
    plot = p.plot(key=key, param="T2M", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="T2M", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="T2M", period=int(fcstDays))
    return render_template('dashboard/climate/t2m.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/ts', methods=['GET','POST'])
def loadDashClimateTs():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="TS")
    min, minDate = s.calcMin(key=key, param="TS")
    std = s.calcStd(key=key, param="TS")
    max, maxDate = s.calcMax(key=key, param="TS")
    plot = p.plot(key=key, param="TS", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="TS", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="TS", period=int(fcstDays))
    return render_template('dashboard/climate/ts.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/qv2m', methods=['GET','POST'])
def loadDashClimateQv2m():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="QV2M")
    min, minDate = s.calcMin(key=key, param="QV2M")
    std = s.calcStd(key=key, param="QV2M")
    max, maxDate = s.calcMax(key=key, param="QV2M")
    plot = p.plot(key=key, param="QV2M", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="QV2M", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="QV2M", period=int(fcstDays))
    return render_template('dashboard/climate/qv2m.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/rh2m', methods=['GET','POST'])
def loadDashClimateRh2m():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="RH2M")
    min, minDate = s.calcMin(key=key, param="RH2M")
    std = s.calcStd(key=key, param="RH2M")
    max, maxDate = s.calcMax(key=key, param="RH2M")
    plot = p.plot(key=key, param="RH2M", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="RH2M", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="RH2M", period=int(fcstDays))
    return render_template('dashboard/climate/rh2m.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )


@app.route('/dashboard/climate/ps', methods=['GET','POST'])
def loadDashClimatePs():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="PS")
    min, minDate = s.calcMin(key=key, param="PS")
    std = s.calcStd(key=key, param="PS")
    max, maxDate = s.calcMax(key=key, param="PS")
    plot = p.plot(key=key, param="PS", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="PS", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="PS", period=int(fcstDays))
    return render_template('dashboard/climate/ps.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/wd2m', methods=['GET','POST'])
def loadDashClimateWd2m():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="WD2M")
    min, minDate = s.calcMin(key=key, param="WD2M")
    std = s.calcStd(key=key, param="WD2M")
    max, maxDate = s.calcMax(key=key, param="WD2M")
    plot = p.plot(key=key, param="WD2M", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="WD2M", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="WD2M", period=int(fcstDays))
    return render_template('dashboard/climate/wd2m.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/cloud_amt_day', methods=['GET','POST'])
def loadDashClimateCloudAmtDay():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="CLOUD_AMT_DAY")
    min, minDate = s.calcMin(key=key, param="CLOUD_AMT_DAY")
    std = s.calcStd(key=key, param="CLOUD_AMT_DAY")
    max, maxDate = s.calcMax(key=key, param="CLOUD_AMT_DAY")
    plot = p.plot(key=key, param="CLOUD_AMT_DAY", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="CLOUD_AMT_DAY", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="CLOUD_AMT_DAY", period=int(fcstDays))
    return render_template('dashboard/climate/cloud_amt_day.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/pw', methods=['GET','POST'])
def loadDashClimatePw():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="PW")
    min, minDate = s.calcMin(key=key, param="PW")
    std = s.calcStd(key=key, param="PW")
    max, maxDate = s.calcMax(key=key, param="PW")
    plot = p.plot(key=key, param="PW", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="PW", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="PW", period=int(fcstDays))
    return render_template('dashboard/climate/pw.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/t2mdew', methods=['GET','POST'])
def loadDashClimateT2mdew():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="T2MDEW")
    min, minDate = s.calcMin(key=key, param="T2MDEW")
    std = s.calcStd(key=key, param="T2MDEW")
    max, maxDate = s.calcMax(key=key, param="T2MDEW")
    plot = p.plot(key=key, param="T2MDEW", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="T2MDEW", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="T2MDEW", period=int(fcstDays))
    return render_template('dashboard/climate/t2mdew.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/frostdays', methods=['GET','POST'])
def loadDashClimateFrostdays():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="FROST_DAYS")
    min, minDate = s.calcMin(key=key, param="FROST_DAYS")
    std = s.calcStd(key=key, param="FROST_DAYS")
    max, maxDate = s.calcMax(key=key, param="FROST_DAYS")
    plot = p.plot(key=key, param="FROST_DAYS", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="FROST_DAYS", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="FROST_DAYS", period=int(fcstDays))
    return render_template('dashboard/climate/frostdays.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/climate/prectotcorr', methods=['GET','POST'])
def loadDashClimatePrectotcorr():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="PRECTOTCORR")
    min, minDate = s.calcMin(key=key, param="PRECTOTCORR")
    std = s.calcStd(key=key, param="PRECTOTCORR")
    max, maxDate = s.calcMax(key=key, param="PRECTOTCORR")
    plot = p.plot(key=key, param="PRECTOTCORR", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="PRECTOTCORR", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="PRECTOTCORR", period=int(fcstDays))
    return render_template('dashboard/climate/prectotcorr.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/soil/gwetprof', methods=['GET','POST'])
def loadDashSoilGwetprof():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="GWETPROF")
    min, minDate = s.calcMin(key=key, param="GWETPROF")
    std = s.calcStd(key=key, param="GWETPROF")
    max, maxDate = s.calcMax(key=key, param="GWETPROF")
    plot = p.plot(key=key, param="GWETPROF", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="GWETPROF", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="GWETPROF", period=int(fcstDays))
    return render_template('dashboard/soil/gwetprof.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )


@app.route('/dashboard/soil/gwetroot', methods=['GET','POST'])
def loadDashSoilGwetroot():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="GWETROOT")
    min, minDate = s.calcMin(key=key, param="GWETROOT")
    std = s.calcStd(key=key, param="GWETROOT")
    max, maxDate = s.calcMax(key=key, param="GWETROOT")
    plot = p.plot(key=key, param="GWETROOT", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="GWETROOT", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="GWETROOT", period=int(fcstDays))
    return render_template('dashboard/soil/gwetroot.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )

@app.route('/dashboard/soil/gwettop', methods=['GET','POST'])
def loadDashSoilGwettop():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="GWETTOP")
    min, minDate = s.calcMin(key=key, param="GWETTOP")
    std = s.calcStd(key=key, param="GWETTOP")
    max, maxDate = s.calcMax(key=key, param="GWETTOP")
    plot = p.plot(key=key, param="GWETTOP", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="GWETTOP", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="GWETTOP", period=int(fcstDays))
    return render_template('dashboard/soil/gwettop.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )


@app.route('/dashboard/soil/zom', methods=['GET','POST'])
def loadDashSoilZom():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        startYear = request.args.get('startYear', default=1995)
        endYear = request.args.get('endYear', default=2024)
        groupBy = request.args.get('groupBy', default="default")
        plotType = request.args.get('plotType', default="scatter")
        fcstDays = request.args.get('fcstDays', default="90")

    avg = s.calcMean(key=key, param="Z0M")
    min, minDate = s.calcMin(key=key, param="Z0M")
    std = s.calcStd(key=key, param="Z0M")
    max, maxDate = s.calcMax(key=key, param="Z0M")
    plot = p.plot(key=key, param="Z0M", 
                  startYear=f"{startYear}0101", endYear=f"{endYear}1231", 
                  groupBy=groupBy, plotType=plotType,
                  color="#e17256")
    fcstPlot = p.fcstPlot(key=key, param="Z0M", period=int(fcstDays),
                        fColor="#533d8f", sColorLow="#00b893", sColorUp="#d62e2e")
    script, div = components(plot)
    scriptFcst, divFcst = components(fcstPlot)
    table = s.showFcstTable(key=key, param="Z0M", period=int(fcstDays))
    return render_template('dashboard/soil/zom.html',
                           rlat = lat,
                           rlon = lon,
                           avg = avg[0],
                           min = min,
                           max = max,
                           std = std[0],
                           minDate = minDate,
                           maxDate = maxDate,
                           script = script,
                           div = div,
                           scriptFcst = scriptFcst,
                           divFcst = divFcst,
                           fcstDays = fcstDays,
                           table = table
                        )


@app.route('/dashboard/agri/parea', methods=['GET','POST'])
def loadDashAgriPhysicalArea():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        year = request.args.get('year', default=None)
        tech = request.args.get('tech', default=None)
        crop = request.args.get('crop', default=None)

    data = s.getCropsData(lat, lon, "physicalArea", tech, year, crop)
    max = data['crop'].max()
    min = data['crop'].min()
    crops = data.to_dict(orient='records')
    data = None

    return render_template('dashboard/agri/parea.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops,
                           max = max,
                           min = min
                        )

@app.route('/dashboard/agri/harea', methods=['GET','POST'])
def loadDashAgriHarvestedArea():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        year = request.args.get('year', default=None)
        tech = request.args.get('tech', default=None)
        crop = request.args.get('crop', default=None)

    data = s.getCropsData(lat, lon, "harvested", tech, year, crop)
    max = data['crop'].max()
    min = data['crop'].min()
    crops = data.to_dict(orient='records')
    data = None

    return render_template('dashboard/agri/harea.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops,
                           max = max,
                           min = min
                        )

@app.route('/dashboard/agri/prod', methods=['GET','POST'])
def loadDashAgriProduction():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        year = request.args.get('year', default=None)
        tech = request.args.get('tech', default=None)
        crop = request.args.get('crop', default=None)

    data = s.getCropsData(lat, lon, "productions", tech, year, crop)
    max = data['crop'].max()
    min = data['crop'].min()
    crops = data.to_dict(orient='records')
    data = None

    return render_template('dashboard/agri/prod.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops,
                           max = max,
                           min = min
                        )

@app.route('/dashboard/agri/yield', methods=['GET','POST'])
def loadDashAgriYield():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default=None)
        year = request.args.get('year', default=None)
        tech = request.args.get('tech', default=None)
        crop = request.args.get('crop', default=None)

    data = s.getCropsData(lat, lon, "yields", tech, year, crop)
    max = data['crop'].max()
    min = data['crop'].min()
    crops = data.to_dict(orient='records')
    data = None

    return render_template('dashboard/agri/yield.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops,
                           max = max,
                           min = min
                        )

@app.route('/dashboard/analysis', methods=['GET','POST'])
def loadDashAnalysisBoard():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default="data")
        key_rad = request.args.get('key_rad', default="data_rad")
        plantingdate =  request.args.get('pd', default="2025-01-01")
        crop =  request.args.get('crop', default="whea")
        tgp = request.args.get('tgp', default="max")
    
    code = a.getCountryCode(lat, lon) # get country code
    today = date.today()

    # Get last parameters update date
    t2mlu = a.getParamLastUpdate("t2m", key)
    prectotcorrlu = a.getParamLastUpdate("prectotcorr", key)
    ws2mlu = a.getParamLastUpdate("WS2M", key)
    evptrnslu = a.getParamLastUpdate("EVPTRNS", key)
    evlandlu = a.getParamLastUpdate("EVLAND", key)

    # get next year start
    nyStart = a.getNextYearStart(key=key)

    # Get parameters last value for those dates
    t2m = a.getParamLastValue("t2m", key)
    prectotcorr = a.getParamLastValue("prectotcorr", key)
    ws2m = a.getParamLastValue("ws2m", key)
    rh2m = a.getParamLastValue("rh2m", key)
    evptrns = a.getParamLastValue("evptrns", key)
    evland = a.getParamLastValue("evland", key)

    # get parameters growth rate
    t2mr, t2ms = a.getParamGrowthRate("t2m", key)
    prectotcorrr, prectotcorrs = a.getParamGrowthRate("prectotcorr", key)
    ws2mr, ws2ms = a.getParamGrowthRate("ws2m", key)
    evptrnsr, evptrnss = a.getParamGrowthRate("evptrns", key)
    evlandr, evlands = a.getParamGrowthRate("evland", key)

    # get parameters last sevent days values for graphs (point level tab)
    t2mInfo = a.getParamLastSevenDaysValues("t2m", key)
    prectotcorrInfo = a.getParamLastSevenDaysValues("prectotcorr", key)
    ws2mInfo = a.getParamLastSevenDaysValues("ws2m", key)
    evptrnsInfo = a.getParamLastSevenDaysValues("evptrns", key)
    evlandInfo = a.getParamLastSevenDaysValues("evland", key)

    # get temperature condition index part elements
    t2mCI = a.getParamConditionIndexValue(key)
    t2mMinVal, t2mMinDate = s.calcMin(key, "t2m")
    t2mMaxVal, t2mMaxDate = s.calcMax(key, "t2m")

    # get mean annual precipitation and monthly precipitation for chart js graph display
    mcap = a.getMeanAnnualParam(key)
    mSumPrecip = a.getMonthlyParamDataSum(key, param="prectotcorr")

    # get precipitation suitability for general agriculture
    pei = a.getPrecipitationEffectivenessIndex(key)
    climateType = a.getClimateTypeFromPei(pei)

    # get HTML table of crops factors
    # kcTable = a.getCropFactorsTable()
    
    # get soil params history mean
    soilParams = a.getSoilParamAgriSuitability(key)
    # get precipitation suitability for general agriculture
    prectotcorrAgriSuitability = a.getPrecipitationSuitabilityAgriculture(key)

    # get radiation data
    # data = a.transformRadiationData(key_rad)

    # get monthly ET0 levels
    mSumEt0 = a.getRadMonthlyParamDataSum(key_rad, param="et0")

    # get history ET0 data
    # et0 = a.getHistoryET0Data(key_rad)

    # get et0 fcst
    #fcst = a.getParamCampaignForecast(key, param="prectotcorr", campaign="ny")

    # get mintgp of crops
    wheaMintgp = a.getCropTotalGrowthPeriod(crop="whea")
    riceMintgp = a.getCropTotalGrowthPeriod(crop="rice")
    maizMintgp = a.getCropTotalGrowthPeriod(crop="maiz")
    pmilMintgp = a.getCropTotalGrowthPeriod(crop="pmil")
    smilMintgp = a.getCropTotalGrowthPeriod(crop="smil")
    sorgMintgp = a.getCropTotalGrowthPeriod(crop="sorg")
    potaMintgp = a.getCropTotalGrowthPeriod(crop="pota")
    swpoMintgp = a.getCropTotalGrowthPeriod(crop="swpo")

    # get fstTableForBpd
    fcstTableForBpd = a.getForecastsTableForPlantingDate()

    # get cropdevelopment dataframe
    table = a.createCropDevelopmentDataFrame(fcstTableForBpd, plantingdate, crop, tgp=tgp)

    # get stage time span
    ipSpan = a.getStageStartAndEndDate(table, stage="ip")
    cdpSpan = a.getStageStartAndEndDate(table, stage="cdp")
    mssSpan = a.getStageStartAndEndDate(table, stage="mss")
    lssSpan = a.getStageStartAndEndDate(table, stage="lss")

    # get Month' water need and precipitation
    wnStages = a.getParamByStage(table, 'water_need')
    precStages = a.getParamByStage(table, 'prectotcorr')
    wnMonth = a.getParamByMonth(table, 'water_need')
    precMonth = a.getParamByMonth(table, 'prectotcorr')

    eor = a.getEffectivenessOfRainfall(wnStages, precStages)

    # get maxtgp of crops
    wheaMaxtgp = a.getCropTotalGrowthPeriod(crop="whea", type='max')
    riceMaxtgp = a.getCropTotalGrowthPeriod(crop="rice", type='max')
    maizMaxtgp = a.getCropTotalGrowthPeriod(crop="maiz", type='max')
    pmilMaxtgp = a.getCropTotalGrowthPeriod(crop="pmil", type='max')
    smilMaxtgp = a.getCropTotalGrowthPeriod(crop="smil", type='max')
    sorgMaxtgp = a.getCropTotalGrowthPeriod(crop="sorg", type='max')
    potaMaxtgp = a.getCropTotalGrowthPeriod(crop="pota", type='max')
    swpoMaxtgp = a.getCropTotalGrowthPeriod(crop="swpo", type='max')

    # get best planting data of crops
    wheaMinBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="whea")
    maizMinBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="maiz")
    pmilMinBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="pmil")
    smilMinBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="smil")
    sorgMinBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="sorg")
    potaMinBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="pota")
    swpoMinBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="swpo")

    wheaMaxBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="whea", type="max")
    maizMaxBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="maiz", type="max")
    pmilMaxBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="pmil", type="max")
    smilMaxBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="smil", type="max")
    sorgMaxBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="sorg", type="max")
    potaMaxBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="pota", type="max")
    swpoMaxBestPd = a.getCropOptimalPlantingDate(dt=fcstTableForBpd, crop="swpo", type="max")

    dtg = predict.getMonthlyData(lat, lon)
    wheaRY = predict.predict(dtg, tech="I", crop="whea")
    wheaIY = predict.predict(dtg, tech="I", crop="whea")

    riceRY = predict.predict(dtg, tech="R", crop="rice")
    riceIY = predict.predict(dtg, tech="I", crop="rice")

    maizRY = predict.predict(dtg, tech="R", crop="maiz")
    maizIY = predict.predict(dtg, tech="I", crop="maiz")

    pmilRY = predict.predict(dtg, tech="R", crop="pmil")
    pmilIY = predict.predict(dtg, tech="I", crop="pmil")

    smilRY = predict.predict(dtg, tech="R", crop="smil")
    smilIY = predict.predict(dtg, tech="I", crop="smil")

    sorgRY = predict.predict(dtg, tech="R", crop="sorg")
    sorgIY = predict.predict(dtg, tech="I", crop="sorg")

    potaRY = predict.predict(dtg, tech="R", crop="pota")
    potaIY = predict.predict(dtg, tech="I", crop="pota")

    swpoRY = predict.predict(dtg, tech="R", crop="swpo")
    swpoIY = predict.predict(dtg, tech="I", crop="swpo")

    dtR = pd.DataFrame({
        "crop": ["Whea", "Rice", "Maiz", "Pmil", "Smil", "Sorg", "Pota", "Swpo"],
        "yield": [wheaRY, riceRY, maizRY, pmilRY, smilRY, sorgRY, potaRY, swpoRY]
    })
    dtR = dtR.sort_values(by='yield', ascending=False)
    rainfedY = {
        'labels': list(dtR["crop"]),
        'values': list(dtR["yield"])
    }

    dtI = pd.DataFrame({
        "crop": ["Whea", "Rice", "Maiz", "Pmil", "Smil", "Sorg", "Pota", "Swpo"],
        "yield": [wheaIY, riceIY, maizIY, pmilIY, smilIY, sorgIY, potaIY, swpoIY]
    })
    dtI = dtI.sort_values(by='yield', ascending=False)
    irrigatedY = {
        'labels': list(dtI["crop"].tolist()),
        'values': list(dtI["yield"].tolist())
    }


    return render_template('dashboard/analysis.html',
                           rlat = lat,
                           rlon = lon,
                           today = today,
                           countryCode = code,
                           LastDate = a.todayDate,
                           t2mlu = t2mlu,
                           prectotcorrlu = prectotcorrlu,
                           ws2mlu = ws2mlu,
                           evptrnslu = evptrnslu,
                           evlandlu = evlandlu,

                           t2m = t2m,
                           prectotcorr = prectotcorr,
                           ws2m = ws2m,
                           rh2m = rh2m,
                           evptrns = evptrns,
                           evland = evland,

                           t2mr = t2mr,
                           prectotcorrr = prectotcorrr,
                           ws2mr = ws2mr,
                           evptrnsr = evptrnsr,
                           evlandr = evlandr,

                           t2ms = t2ms,
                           prectotcorrs = prectotcorrs,
                           ws2ms = ws2ms,
                           evptrnss = evptrnss,
                           evlands = evlands,

                           t2mInfo = t2mInfo,
                           prectotcorrInfo = prectotcorrInfo,
                           ws2mInfo = ws2mInfo,
                           evptrnsInfo = evptrnsInfo,
                           evlandInfo = evlandInfo,

                           t2mCI = t2mCI,

                           t2mMinVal = t2mMinVal,
                           t2mMinDate = t2mMinDate,
                           t2mMaxVal = t2mMaxVal,
                           t2mMaxDate = t2mMaxDate,

                           nyStart = nyStart,

                           mcap = mcap,
                           mSumPrecip = mSumPrecip,

                           pei = pei,
                           climateType = climateType,
                        #    kcTable = kcTable
                           gwetprofAgriSuitability = soilParams[0],
                           gwetrootAgriSuitability = soilParams[1],
                           gwettopAgriSuitability = soilParams[2],
                           prectotcorrAgriSuitability = prectotcorrAgriSuitability,
                           gSuitability = round(0.04 * soilParams[0] + 0.07 * soilParams[1] + 0.09 * soilParams[2] + 0.8 * prectotcorrAgriSuitability, 2),
                           mSumEt0 = mSumEt0,

                           wheaMintgp = wheaMintgp,
                           riceMintgp = riceMintgp,
                           maizMintgp = maizMintgp,
                           pmilMintgp = pmilMintgp,
                           smilMintgp = smilMintgp,
                           sorgMintgp = sorgMintgp,
                           potaMintgp = potaMintgp,
                           swpoMintgp = swpoMintgp,

                           wheaMaxtgp = wheaMaxtgp,
                           riceMaxtgp = riceMaxtgp,
                           maizMaxtgp = maizMaxtgp,
                           pmilMaxtgp = pmilMaxtgp,
                           smilMaxtgp = smilMaxtgp,
                           sorgMaxtgp = sorgMaxtgp,
                           potaMaxtgp = potaMaxtgp,
                           swpoMaxtgp = swpoMaxtgp,

                           wheaMinBestPd = wheaMinBestPd,
                           maizMinBestPd = maizMinBestPd,
                           pmilMinBestPd = pmilMinBestPd,
                           smilMinBestPd = smilMinBestPd,
                           sorgMinBestPd = sorgMinBestPd,
                           potaMinBestPd = potaMinBestPd,
                           swpoMinBestPd = swpoMinBestPd,

                           wheaMaxBestPd = wheaMaxBestPd,
                           maizMaxBestPd = maizMaxBestPd,
                           pmilMaxBestPd = pmilMaxBestPd,
                           smilMaxBestPd = smilMaxBestPd,
                           sorgMaxBestPd = sorgMaxBestPd,
                           potaMaxBestPd = potaMaxBestPd,
                           swpoMaxBestPd = swpoMaxBestPd,

                           ipSpan = ipSpan,
                           cdpSpan = cdpSpan,
                           mssSpan = mssSpan,
                           lssSpan = lssSpan,

                           wnStages = wnStages,
                           precStages = precStages,
                           wnMonth = wnMonth,
                           precMonth = precMonth,

                           eor = eor,
                           dtg = dtg,

                           rainfedY = rainfedY,
                           irrigatedY = irrigatedY
                        )




@app.route('/dashboard/land', methods=['GET','POST'])
def loadDashLandscapeBoard():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default="data")
        key_rad = request.args.get('key_rad', default="data_rad")
        imgd = request.args.get('imgd', default=date.today().strftime("%Y-%m-%d"))
        param = request.args.get('param', default="default")
        pld = request.args.get('pd', default=date.today().strftime("%Y-%m-%d"))
        crop = request.args.get('crop', default="whea")

    nyStart = a.getNextYearStart(key=key)
    today = date.today()
    one_week = pd.to_datetime(imgd) - timedelta(weeks=1)

    aoi = l.getFieldBBox(lat, lon, res=10)
    image = l.getImage(aoi, param, time_interval=(one_week.strftime("%Y-%m-%d"), imgd))
    map = l.getMap(image, aoi)
    iframe = map.get_root()._repr_html_()
    # cloudCover = l.calculateCloudCover(aoi, time_interval=(one_week.strftime("%Y-%m-%d"), imgd))

    legend = l.getHtmlLegend(param=param)
    target, use = l.getTargetedParameter(param=param)

    cdData = l.createCropDevelopmentDataFrame(pld, crop)
    script, div = l.getPlot(cdData, variables=["Water Need", "Rainfall"])

    return render_template('dashboard/land.html',
                           rlat = lat,
                           rlon = lon,
                           nyStart = nyStart,
                           today = today,
                           iframe = iframe,
                           #cloudCover = cloudCover,
                           legend = legend,
                           param = param.upper(),
                           imgd = imgd,
                           target = target,
                           use = use,
                           script = script,
                           div = div,
                           cdData = cdData
                        )



@app.route('/dashboard/tasks', methods=['GET','POST'])
def loadDashTaskBoard():
    if request.method == 'POST':
        lon = request.form['lon']
        lat = request.form['lat']
    else:
        lon = request.args.get('lon', default=None)
        lat = request.args.get('lat', default=None)
        key = request.args.get('key', default="data")
        key_rad = request.args.get('key_rad', default="data_rad")
        imgd = request.args.get('imgd', default=date.today().strftime("%Y-%m-%d"))
        param = request.args.get('param', default="default")
        pld = request.args.get('pd', default=date.today().strftime("%Y-%m-%d"))
        crop = request.args.get('crop', default="whea")

    today = date.today()
    nyStart = a.getNextYearStart(key=key)

    

    return render_template('dashboard/tasks.html',
                           rlat = lat,
                           rlon = lon,
                           today = today,
                           nyStart = nyStart
                        )







if __name__ == '__main__':
    app.run(debug=True)