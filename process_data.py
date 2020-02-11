# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:40:50 2020

@author: jidong
"""

import pandas as pd

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
    wholetable.to_csv('latest_data.csv')
    print (latest_data)
    return 
    
    
    
    
def read_ts_JHU(data):
    return
    
    
    

if __name__ == "__main__":
    JHUurl = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/time_series/")
    data = [pd.read_csv(JHUurl+"time_series_2019-ncov-Confirmed.csv"),pd.read_csv(JHUurl+"time_series_2019-ncov-Deaths.csv"),pd.read_csv(JHUurl+"time_series_2019-ncov-Recovered.csv")]
    get_latest_JHU(data)