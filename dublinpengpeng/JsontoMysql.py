#!/usr/bin/env python
# coding: utf-8


import os
import json
import pymysql
import sqlalchemy as sqla
from sqlalchemy import create_engine
import requests
import traceback
import datetime
import time

URI = "dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com"
PORT = "3306"
DB = "dublin"
USER = "root"
PASSWORD = "shuyuqian"

SQL_CREATE_DB = "CREATE DATABASE IF NOT EXISTS dublin;"

SQL_CREATE_STATIC = '''
CREATE TABLE IF NOT EXISTS station(
address VARCHAR(256),
banking INTEGER,
bike_stands INTEGER,
bonus INTEGER,
contract_name VARCHAR(256),
name VARCHAR(256),
number INTEGER,
position_lat REAL,
position_lng REAL,
status VARCHAR(256)
)'''

SQL_CREATE_DYNAMIC = '''
CREATE TABLE IF NOT EXISTS availability(
datetime VARCHAR(256),
number INTEGER, 
available_bikes INTEGER, 
available_bike_stands INTEGER, 
last_update INTEGER)
'''

NAME = "Dublin"
STATIONS = "https://api.jcdecaux.com/vls/v1/stations"
APIKEY = "30af517cf938432caf25e8fe0fa46fedf2fc6e41"


# do validation and checks before insert
def validate_string(val):
    if val != None:
        if type(val) is int:
            # for x in val:
            #   print(x)
            return str(val).encode('utf-8')
        else:
            return val

def main():

    engine = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB), echo=True)
    engine.execute(SQL_CREATE_DB)

    def station_to_db(text):
        try:
            res = engine.execute("DROP TABLE IF EXISTS station")
            res = engine.execute(SQL_CREATE_STATIC)
            print(res.fetchall())
        except Exception as e:
            print(e)
        stations = json.loads(text)
        print(type(stations), len(stations))
        for station in stations:
            print(station)
            vals = (station.get('address'), int(station.get('banking')),
                    station.get('bike_stands'), int(station.get('bonus')),
                    int(station.get('last_update')), station.get('contract_name'),
                    int(station.get('number')), station.get('position').get('lat'),
                    station.get('position').get('lng'), station.get('status'))
            engine.execute("insert into station values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
        return

    def availability_to_db(text):
        try:
            res = engine.execute(SQL_CREATE_DYNAMIC)
            print(res.fetchall())
        except Exception as e:
            print(e)
        stations = json.loads(text)
        print(type(stations), len(stations))
        for station in stations:
            print(station)
            timestampStr = now.strftime("%d-%b-%Y (%H:%M:%S.%f)")
            vals = (timestampStr, int(station.get('number')), int(station.get('available_bikes')),
                    int(station.get('available_bike_stands')), int(station.get('bonus')),
                    )
            engine.execute("insert into availability values(%s,%s,%s,%s,%s)", vals)
        return

    while True:
        # try:
        now = datetime.datetime.now()
        r = requests.get(STATIONS, params={"apiKey": APIKEY, "contract": NAME})
        print(r, now)
        station_to_db(r.text)
        availability_to_db(r.text)
        time.sleep(30*60)
        # except:
        #     print(traceback.format_exc())
    return

if __name__ == '__main__':
    main()
