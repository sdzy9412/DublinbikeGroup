#!/usr/bin/env python
#!/usr/bin/env python
#!/usr/bin/env python
# coding: utf-8



import json
import pymysql

def main():
    #try:
    with open('dublin.json') as json_data:
        json_obj = json.load(json_data)



    # do validation and checks before insert
    def validate_string(val):
        if val != None:
            if type(val) is int:
                return str(val).encode('utf-8')
            else:
                return val

            
    # connect to MySQL
    con = pymysql.connect(host='dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com', user='root', passwd='shuyuqian', db='dublin')
    cursor = con.cursor()


    cursor.execute(
        "CREATE TABLE `dublin`.`dublinbike_static` ( `number` INT NULL,  `name` VARCHAR(45) NULL,  `address` VARCHAR(45) NULL,  `latitude` VARCHAR(45) NULL,  `longitude` VARCHAR(45) NULL);")
    # parse json data to SQL insert
    for i, item in enumerate(json_obj):
        number = validate_string(item.get("number", None))
        name = validate_string(item.get("name", None))
        address = validate_string(item.get("address", None))
        latitude = validate_string(item.get("latitude", None))
        longitude = validate_string(item.get("longitude", None))


        cursor.execute(
            "INSERT INTO dublinbike_static (number,	name,	address,	latitude,	longitude) VALUES (%s,	%s,	%s,	%s,	%s)",    (number, name, address, latitude, longitude))
    con.commit()
    con.close()

#     except:
#             print("Unable to get information.")
#     return


if __name__ == '__main__':
    main()
