#!/usr/bin/env python
# coding: utf-8

# # Data Collection
# 

# This charpter is aim to describe how to collect the data
# Collected data including bike occupation situation and weather information

# In[1]:


import requests
from datetime import datetime
import pymysql
import traceback


# In[2]:


url='http://api.openweathermap.org/data/2.5/weather?q=Dublin,ie&units=metric&APPID=7c4d32959a99216eeb3c99efc8000278'
weatherDataString=requests.get(url=url)
wds = weatherDataString.json()


# In[3]:


wds
currentTime = datetime.now().strftime('%Y-%m-%d %H:%M')


# In[36]:


#store each piece of data from the weather info json as a variable so that we may later store it in out MySQL DB
#most data will be whole numbers - we have rounded up any decimals to simplify data storage in the DB
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

#wind gust is not always present so we place it in a try/except block
try:
    windGust = round(wds['wind']['gust'])
    weatherDataSQL += "'" + str(windGust) + "',"
    isWindGust = True
except:
    pass

clouds = wds['clouds']['all']
weatherDataSQL += "'" + str(clouds) + "')"

#pick appropriate statement depending on whether there is windGust or not
if isWindGust: # requied to change
    insertStatement = "INSERT INTO Weather (dateTime, weatherID, weatherMain, weatherDescr, weatherIcon, temperature, pressure, humidity, tempMin, tempMax, visibility, windSpeed, windDeg, windGust, clouds) VALUES ("
else:
    insertStatement = "INSERT INTO Weather (dateTime, weatherID, weatherMain, weatherDescr, weatherIcon, temperature, pressure, humidity, tempMin, tempMax, visibility, windSpeed, windDeg, clouds) VALUES ("

insertStatement += weatherDataSQL


# In[6]:


isWindGust=True


# In[46]:


creat_table_test="CREATE TABLE Weather(dateTime DATETIME, weatherID int, weatherMain varchar(255), weatherDescr varchar(255), weatherIcon varchar(255), temperature int, pressure int, humidity int, tempMin int ,tempMax int, visibility int, windSpeed int, winDeg int, windGust int, clouds int);"
        


# In[50]:


host="dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com"
port=3306
dbname="dublin"
user="root"
password="shuyuqian"


# In[48]:


insertStatement = "INSERT INTO Weather (dateTime,weatherID,weatherMain,weatherDescr, weatherIcon, temperature, pressure, humidity, tempMin, tempMax, visibility, windSpeed) VALUES('2020-02-18 12:18', '500','Rain','light rain','10d','7','1010','87','6','7','10000','7')"


# In[49]:


conn = pymysql.connect(host, user=user,port=port, passwd=password, db=dbname)
#this creates a cursor object that you need to execute operations on the DB
#cursorObject = conn.cursor()
cursorObject = conn.cursor()
#executes the insert statement defined above - note you also have to commit it for it to take effect
#cursorObject.execute(insertStatement)
#cursorObject.execute(creat_table_test)
cursorObject.execute(insertStatement)
#this is necessary to make the changes executed above take place
conn.commit()
#closes the connection to the DB
conn.close()


# In[52]:


insertStatement


# In[ ]:




