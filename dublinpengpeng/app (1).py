'''environment variable setting in terminal:

export FLASK_APP = app.py
flask run
export FLASK_DEBUG = 1 (set flask to debug mode)
'''

from flask import Flask, render_template
import json
app = Flask(__name__)

# class Station:
#     def __init__(self, num, name, lat, lng):
#         self.num  = num
#         self.name = name
#         self.lat  = lat
#         self.lng  = lng

with open("dublin.json") as json_data:
    station_file = json.load(json_data)

bike_station = []

for station in station_file:
    bike_station.append([station.get('number'), station.get('name'), station.get('latitude'), station.get('longitude')])
length = len(bike_station)

@app.route("/")
def index():
    return render_template("dinner.html", bike_station=bike_station, length=length)
print(bike_station[0][1])

if __name__ == '__main__':
    app.run(host="localhost", debug=True)
