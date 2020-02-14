# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:40:50 2020

@author: jidong
"""

import pandas as pd
import json
from urllib.request import urlopen, quote

def get_latest_JHU(data):
    wholetable = pd.DataFrame()
    keylist = ['Confirmed','Deaths','Recovered']
    for num, dataset in enumerate(data, start=0):
        dataset = dataset.iloc[:,[0,1,2,3,-1]]
        latest_data = list(dataset)[-1]
        dataset.rename(columns={list(dataset)[-1]:keylist[num]}, inplace=True)
        if len(wholetable)==0:
            wholetable = dataset
        else:
            wholetable = pd.merge(wholetable,dataset,on = ['Province/State','Country/Region','Lat','Long'])
    wholetable.rename(columns = {"Lat":"Latitude","Long":"Longitude"}, inplace = True)
    wholetable.loc[wholetable['Country/Region'].isin (['Mainland China','Taiwan','Hong Kong','Macau']), 'Country/Region'] = "China"
    wholetable.to_csv('latest_data_JHU.csv')
    print (latest_data)
    return 
    
    
    
    
def read_ts_JHU(data):
    return
    

def get_latest_dxy(data):
    data = data.sort_values('updateTime').groupby(['provinceName','cityName']).tail(1).reset_index().drop(columns=['index'])
    data['Latitude'] = float("NaN")
    data["Longitude"] = float("NaN")
    searchfor = ['外地来','明确地区','不明地区','未知地区','未知','人员','待明确']
    data = data[~data['cityName'].str.contains('|'.join(searchfor))]
    data = data[~data['provinceName'].str.contains('|'.join(['香港','台湾','澳门']))]
    for indexs in data.index:
        address = data.loc[indexs,'provinceName']+data.loc[indexs,'cityName']
        get_location = get_location_using_baidu(address)
        get_lat = get_location[0]
        get_lng = get_location[1]
        data.loc[indexs,'Latitude'] = get_lat
        data.loc[indexs,'Longitude'] = get_lng
    print (data)
    data.to_csv('latest_data_DXY.csv')
    return
        
def get_location_using_baidu(address):
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = '2OBdehyusfGE2KRAvik4jhzb0gQ1VgfA'
    address = quote(address)
    uri = url + '?' + 'address=' + address  + '&output=' + output + '&ak=' + ak
    req = urlopen(uri)
    res = req.read().decode() 
    temp = json.loads(res)
    lat = temp['result']['location']['lat']
    lng = temp['result']['location']['lng']
    return lat,lng

def integrate_dxy_and_JHU(JHUpath,dxypath):
    jhudata = pd.read_csv(JHUpath).iloc[:, 1:]
    dxydata = pd.read_csv(dxypath).iloc[:, [1,2,7,9,10,12,13]]
    indexNames = jhudata[(jhudata['Country/Region'] == 'China') & (~jhudata['Province/State'].isin(['Taiwan','Hong Kong','Macau']))].index
    jhudata.drop(indexNames , inplace=True)
    dxydata.loc[:,'Province/State'] = dxydata["provinceName"] + dxydata["cityName"]
    dxydata.loc[:,'Country/Region'] = 'China'
    dxydata = dxydata.iloc[:,2:]
    dxydata.columns = ['Confirmed','Recovered','Deaths','Latitude','Longitude', 'Province/State', 'Country/Region']
    dxydata = dxydata[jhudata.columns]
    wholetable = pd.concat([jhudata, dxydata], ignore_index = True)
    wholetable.loc[:,'tail'] = ''
    wholetable.to_csv('integrated.csv')
    return

if __name__ == "__main__":
    JHUurl = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/time_series/")
    data = [pd.read_csv(JHUurl+"time_series_2019-ncov-Confirmed.csv"),pd.read_csv(JHUurl+"time_series_2019-ncov-Deaths.csv"),pd.read_csv(JHUurl+"time_series_2019-ncov-Recovered.csv")]
    get_latest_JHU(data)
    #data = pd.read_csv("https://raw.githubusercontent.com/BlankerL/DXY-COVID-19-Data/master/csv/DXYArea.csv")
    #get_latest_dxy(data)
    integrate_dxy_and_JHU('latest_data_JHU.csv','latest_data_DXY.csv')