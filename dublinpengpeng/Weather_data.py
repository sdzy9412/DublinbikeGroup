#!/usr/bin/env python
# coding: utf-8

# # Data Collection
# 

# This charpter is aim to describe how to collect the data
# Collected data including bike occupation situation and weather information

# In[2]:


import requests
from datetime import datetime
import pymysql
import traceback
import time


# In[3]:


def weather_info():
    # fetch weather info
    url='http://api.openweathermap.org/data/2.5/weather?q=Dublin,ie&units=metric&APPID=7c4d32959a99216eeb3c99efc8000278'
    weatherDataString=requests.get(url=url)
    wds = weatherDataString.json()
    
    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M')
    weatherDataSQL = ""
    weatherDataSQL += "'" + currentTime + "',"

    weatherID = str(wds['weather'][0]['id'])
    weatherDataSQL += "'" + weatherID + "',"

    weatherMain = wds['weather'][0]['main']
    weatherDataSQL += "'" + weatherMain + "',"

    weatherDescr = wds['weather'][0]['description']
    weatherDataSQL += "'" + weatherDescr + "',"

    weatherIcon = wds['weather'][0]['icon']
    weatherDataSQL += "'" + weatherIcon + "',"

    temp = round(wds['main']['temp'])
    weatherDataSQL += "'" + str(temp) + "',"

    pressure = wds['main']['pressure']
    weatherDataSQL += "'" + str(pressure) + "',"

    humidity = round(wds['main']['humidity'])
    weatherDataSQL += "'" + str(humidity) + "',"

    tempMin = round(wds['main']['temp_min'])
    weatherDataSQL += "'" + str(tempMin) + "',"

    tempMax = round(wds['main']['temp_max'])
    weatherDataSQL += "'" + str(tempMax) + "',"

    visibility = round(wds['visibility'])
    weatherDataSQL += "'" + str(visibility) + "',"

    windSpeed = round(wds['wind']['speed'])
    weatherDataSQL += "'" + str(windSpeed) + "',"

    windDegree = round(wds['wind']['deg'])
    weatherDataSQL += "'" + str(windDegree) + "',"

    clouds = wds['clouds']['all']
    weatherDataSQL += "'" + str(clouds) + "')"


    insertStatement = "INSERT INTO Weather (dateTime, weatherID, weatherMain, weatherDescr, weatherIcon, temperature, pressure, humidity, tempMin, tempMax, visibility, windSpeed, windDeg, clouds) VALUES ("

    insertStatement += weatherDataSQL
    return insertStatement

def write_db(String):
    conn = pymysql.connect(host, user=user,port=port, passwd=password, db=dbname)
    cursorObject = conn.cursor()
    cursorObject.execute(String)
    conn.commit()
    conn.close()


# In[4]:


creat_table="CREATE TABLE IF NOT EXISTS Weather(dateTime DATETIME, weatherID int, weatherMain varchar(255), weatherDescr varchar(255), weatherIcon varchar(255), temperature int, pressure int, humidity int, tempMin int ,tempMax int, visibility int, windSpeed int, windDeg int, clouds int);"
        


# In[5]:


host="dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com"
port=3306
dbname="dublin"
user="root"
password="shuyuqian"


# Create Table for the first time. 

# In[6]:


conn = pymysql.connect(host, user=user,port=port, passwd=password, db=dbname)
cursorObject = conn.cursor()
insertStatement=weather_info()

cursorObject.execute(creat_table)
cursorObject.execute(insertStatement)

conn.commit()
conn.close()


# Fetch weather and store into database dynamically.

# In[8]:


while True:
    # fetch data dynamically
    time.sleep(180*60) # the time period is  3hrs and it can be changed.
    winfo=weather_info()
    write_db(winfo)

