#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import pandas as pd
import pymysql

# In[2]:

def main():
    # try:
    with open('dublin.json') as json_data:
        json_obj = json.load(json_data)


    # In[3]:


    # do validation and checks before insert
    def validate_string(val):
        if val != None:
            if type(val) is int:
                # for x in val:
                #   print(x)
                return str(val).encode('utf-8')
            else:
                return val


    # In[4]:


    # connect to MySQL
    con = pymysql.connect(host='dublinbike.cx8vz93uf5cv.eu-west-1.rds.amazonaws.com', user='admin', passwd='pengpeng', db='dublinbike')
    cursor = con.cursor()

    # In[5]:


    #     latitude = validate_string(item.get("latitude", None))
    #     longitude = validate_string(item.get("longitude", None))
    #     cursor.execute("INSERT INTO dublinbike_static (number, name, address) VALUES (%s,%s,$s)", (number, name, address))
    #     cursor.execute("INSERT INTO dublinbike_static (number,	name,	address,	latitude,	longitude) VALUES (%s,	%s,	%s,	%s,	%s)", (number,	name,	address,	latitude,	longitude))


    # In[6]:

    cursor.execute(
        "CREATE TABLE `dublinbike`.`dublinbike_static1` ( `number` INT NULL,  `name` VARCHAR(45) NULL,  `address` VARCHAR(45) NULL,  `latitude` VARCHAR(45) NULL,  `longitude` VARCHAR(45) NULL);")
    # parse json data to SQL insert
    for i, item in enumerate(json_obj):
        number = validate_string(item.get("number", None))
        name = validate_string(item.get("name", None))
        address = validate_string(item.get("address", None))
        latitude = validate_string(item.get("latitude", None))
        longitude = validate_string(item.get("longitude", None))


        cursor.execute(
            "INSERT INTO dublinbike_static1 (number,	name,	address,	latitude,	longitude) VALUES (%s,	%s,	%s,	%s,	%s)",    (number, name, address, latitude, longitude))
    con.commit()
    con.close()

        # In[ ]:
    # except:
    #         print("Unable to get information.")
    # return


if __name__ == '__main__':
    main()

