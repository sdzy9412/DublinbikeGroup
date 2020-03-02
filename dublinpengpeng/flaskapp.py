'''environment variable setting in terminal:

export FLASK_APP = flaskapp.py
flask run
export FLASK_DEBUG = 1 (set flask to debug mode)
'''

from flask import Flask, render_template, jsonify
import pymysql

app = Flask(__name__,static_url_path='')
# app.config.from_object('config')

def connect_to_database():
    conn = pymysql.connect(host='dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com', user='root', passwd='shuyuqian',db='new_connection')
    return conn

# with open("dublin.json") as json_data:
#     station_file = json.load(json_data)
#
# bike_station = []
#
# for station in station_file:
#     bike_station.append([station.get('number'), station.get('name'), station.get('latitude'), station.get('longitude')])
# length = len(bike_station)

@app.route("/")
def index():
    # return render_template("index.html", bike_station=bike_station, length=length)
    #return render_template('index.html',MAPS_APIKEY = app.config["MAPS_APIKEY"])
    return render_template('showmarker.html')

@app.route("/stations", methods=['GET', 'POST'])
def get_station():
    conn = connect_to_database()
    cur = conn.cursor()
    stations = []
    cur.execute("SELECT * FROM dublinbike_static;")
    rows = cur.fetchall()
    for row in rows:
        stations.append(row)
    return jsonify(stations = stations)

if __name__ == '__main__':
    app.run(host="localhost", debug=True)
