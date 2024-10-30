from flask import Flask, request, render_template, redirect, url_for, jsonify
import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components


from extern import fetch as f
from extern.dash.clim import statClim as stc
from extern.dash.clim import plotClim as ptc
from extern.dash.soil import statSoil as sts
from extern.dash.soil import plotSoil as pts
from extern.dash.params import stat as s
from extern.dash.params import plot as p

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

    f.coords[0] = lat
    f.coords[1] = lon
    data = f.getCachedData(lat, lon)
    if data:
        pass
    else:
        data = f.getPointData(lat, lon)
    
    f.dtDict.clear()
    f.dtDict["data"] = data
    return render_template('dashboard/home.html',rlon = lon, rlat = lat, lon=round(float(lon), 2), lat=round(float(lat), 2))

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
    crops = data.to_dict(orient='records')

    return render_template('dashboard/agri/parea.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops
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
    crops = data.to_dict(orient='records')

    return render_template('dashboard/agri/harea.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops
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
    crops = data.to_dict(orient='records')

    return render_template('dashboard/agri/prod.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops
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
    crops = data.to_dict(orient='records')

    return render_template('dashboard/agri/yield.html',
                           rlat = lat,
                           rlon = lon, 
                           crops = crops
                        )






if __name__ == '__main__':
    app.run(debug=True)