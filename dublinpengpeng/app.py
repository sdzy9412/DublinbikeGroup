# coding: utf-8
'''environment variable setting in terminal:

export FLASK_APP = flaskapp.py
flask run
export FLASK_DEBUG = 1 (set flask to debug mode)
'''
import requests
from flask import Flask, g, render_template, jsonify,json, request
from flask import session, redirect, url_for
import pymysql
from sqlalchemy import create_engine
import pickle
from _datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, EqualTo
import os



import sklearn
app = Flask(__name__,static_url_path='')
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'

USER = 'root'
PASSWORD = 'shuyuqian'
URI = 'dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com'
PORT = '3306'
DB = 'dublin'

def connect_to_database():
    engine = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(USER,PASSWORD,URI,PORT,DB), echo=True)
    return engine

def get_db():
    db = getattr(g, '_datbase', None)
    if db is None:
        db = g._datase = connect_to_database()
        return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

weatherQuery = "SELECT * FROM Weather WHERE dateTime=(SELECT MAX(dateTime) FROM Weather);"
DynamicInfo = "select * from availability order by datetime desc limit 110;"

users = [
            {"id": 1, "full_name": "Ruby", "email": "Burrito@gmail.com", "password": "taco"},
        ]

class SignUpForm(FlaskForm):
    full_name = StringField('Full Name', validators = [InputRequired()])
    email = StringField('Email',
                        validators = [InputRequired(), Email()])
    password = PasswordField('Password', validators = [InputRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators = [InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators = [InputRequired(), Email()])
    password = PasswordField('Password', validators = [InputRequired()])
    submit = SubmitField('Login')

@app.route("/")
def root():
    return render_template("testui.html")

@app.route("/uitest")
def ui():
    return render_template("testui.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        new_user = {"id": len(users)+1, "full_name": form.full_name.data, "email": form.email.data, "password": form.password.data}
        users.append(new_user)
        return render_template("signup.html", message = "Successfully signed up")
    return render_template("signup.html", form = form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = next((user for user in users if user["email"] == form.email.data and user["password"] == form.password.data), None)
        if user is None:
            return render_template("login.html", form = form, message = "Wrong Credentials. Please Try Again.")
        else:
            session['user'] = user
            user_full_name = user["full_name"]
            user_id = user["id"]
            user_email = user["email"]
            return render_template("testui.html", user_full_name = user_full_name, user_id = user_id, user_email = user_email)
    return render_template("login.html", form = form)

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('ui'))

@app.route("/stations")
def get_station():
    engine = get_db()
    stations = []
    StaticInfo = "SELECT * FROM dublinbike_static;"
    rows = engine.execute(StaticInfo)
    for row in rows:
        stations.append(dict(row))

    return jsonify(stations = stations)

@app.route("/available")
def get_available():
    engine = get_db()
    available = []
    DynamicInfo = "SELECT * FROM availability order by last_update desc limit 110;"
    rows = engine.execute(DynamicInfo)
    for row in rows:
        available.append(dict(row))

    return jsonify(available = available)


@app.route("/available/<int:station_id>")
def get_availableid(station_id):
    engine = get_db()
    availableid = []
    sql = "SELECT * FROM availability where number = {};".format(station_id)
    rows = engine.execute(sql)
    for row in rows:
        availableid.append(dict(row))

    return jsonify(availableid=availableid)


@app.route("/weather")
def get_weather():
    engine = get_db()
    weather = []
    sql = "SELECT * FROM Weather WHERE dateTime=(SELECT MAX(dateTime) FROM Weather);"
    rows = engine.execute(sql)
    for row in rows:
        weather.append(dict(row))

    return jsonify(weather=weather)

@app.route("/predict", methods=['POST'])
def prediction_model():
    """
    this part is to get the predicted data (available bikes and stands)
    :return:
    """
    #get the data from the front end
    pick = request.form["pick"]
    pickdate = request.form["pickdate"]
    picktime = request.form["picktime"]
    drop = request.form["drop"]
    dropdate = request.form["dropdate"]
    droptime = request.form["droptime"]

    #distinct post according to the data from front end.
    if picktime == '':
        post = [drop,dropdate+" "+droptime]
    elif droptime == '':
        post =  [pick,pickdate+" "+picktime]
    elif picktime != '' and droptime != '':
        post = [pick, pickdate + " " + picktime, drop, dropdate + " " + droptime]

    def allweatherdata():
        """
        get all the predicted weather data from api
        :return:
        """
        url = 'http://api.openweathermap.org/data/2.5/forecast?q=Dublin,ie&units=metric&APPID=7c4d32959a99216eeb3c99efc8000278'  # 目前这个url可用
        weatherDataString = requests.get(url=url)
        allweather = weatherDataString.json()
        return allweather

    def getselectedweatherdata(length, allweather, selectedtime, selectedweatherlist):
        three_hours_from_input = selectedtime + timedelta(hours=1.5)
        three_hours_to_input = selectedtime - timedelta(hours=1.5)
        for i in range(0, length):  # length=len(allweather['list']
            time = allweather['list'][i]['dt_txt']
            time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            if (three_hours_from_input > time_datetime > three_hours_to_input):
                temp = allweather['list'][i]['main']['temp']
                cloud = allweather['list'][i]['weather'][0]['main']
                speed = allweather['list'][i]['wind']['speed']
                selectedweatherlist.extend((temp, cloud, speed))
        return selectedweatherlist

    def getallweatherdata(inputtime, three_hours_from,three_hours_to, length, allweather, weatherdatalist):
        for i in range(0, length):
            time = allweather['list'][i]['dt_txt']
            time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            if (three_hours_from > time_datetime > three_hours_to):
                temp = allweather['list'][i]['main']['temp']
                cloud = allweather['list'][i]['weather'][0]['main']
                speed = allweather['list'][i]['wind']['speed']
                weatherdatalist.extend((str(inputtime), temp, cloud, speed))
        return weatherdatalist

    def weatherdata(post):
        """
        return the weather data list according to input time.
        and we will give the a time range from an hour and a half before to an hour and a half to the selected time
        :param post:
        :return:
        """
        allweather = allweatherdata()
        selectedweatherlist =[]
        weatherdatalists = []
        length = len(allweather['list'])
        if(len(post)==2):#only pickup or drop off station
            selectedtime = datetime.strptime(post[1], '%Y-%m-%d %H:%M')
            selectedweatherlist = getselectedweatherdata(length, allweather, selectedtime, selectedweatherlist)

            inputtime = datetime.strptime(post[1], '%Y-%m-%d %H:%M') - timedelta(hours=3)
            for k in range(5):
                weatherdatalist = []
                inputtime = inputtime + timedelta(hours=1)
                three_hours_from_input = inputtime + timedelta(hours=1.5)
                three_hours_to_input = inputtime - timedelta(hours=1.5)
                weatherdatalist = getallweatherdata(inputtime, three_hours_from_input, three_hours_to_input, length, allweather, weatherdatalist)
                weatherdatalists.append(weatherdatalist)
            return weatherdatalists,selectedweatherlist
        elif(len(post)==4): #both pickup and dropoff station
            selectedweather = []
            selectedtime_start = datetime.strptime(post[1], '%Y-%m-%d %H:%M')
            selectedtime_end = datetime.strptime(post[3], '%Y-%m-%d %H:%M')
            selectedweather = getselectedweatherdata(length, allweather, selectedtime_start, selectedweather)  # pickup station
            selectedweather = getselectedweatherdata(length, allweather, selectedtime_end, selectedweather)  # dropoff station
            selectedweatherlist.extend(selectedweather)
            inputtime_start = datetime.strptime(post[1], '%Y-%m-%d %H:%M') - timedelta(hours=3)
            inputtime_end = datetime.strptime(post[3], '%Y-%m-%d %H:%M') - timedelta(hours=3)
            for k in range(5):
                weatherdatalist = []
                inputtime_start = inputtime_start+ timedelta(hours=1)
                inputtime_end = inputtime_end + timedelta(hours=1)
                three_hours_from_start = inputtime_start + timedelta(hours=1.5)
                three_hours_to_start = inputtime_start - timedelta(hours=1.5)
                three_hours_from_end = inputtime_end + timedelta(hours=1.5)
                three_hours_to_end = inputtime_end - timedelta(hours=1.5)
                weatherdatalist=getallweatherdata(inputtime_start, three_hours_from_start, three_hours_to_start, length, allweather, weatherdatalist)
                weatherdatalist = getallweatherdata(inputtime_end, three_hours_from_end, three_hours_to_end, length, allweather, weatherdatalist)
                weatherdatalists.append(weatherdatalist)

            return weatherdatalists,selectedweatherlist

    weatherdatalists, selectedweather = weatherdata(post)


    #The second part: for prediction
    random_forest_bikes = pickle.load(open(os.path.abspath("final_prediction_bike.pickle"), 'rb'))
    random_forest_stands = pickle.load(open(os.path.abspath("final_prediction_bike_stands.pickle"), "rb"))
    result = []
    resultlist = []
    timeall=[]

    def weekday_weather(weekday, weather):
        monday = tuesday = wednesday = thursday = friday = saturday = sunday = 0
        clear = clouds = drizzle = mist = rain = 0
        if (weekday == "0"):
            monday = 1
        if (weekday == "1"):
            tuesday = 1
        if (weekday == "2"):
            wednesday = 1
        if (weekday == "3"):
            thursday = 1
        if (weekday == "4"):
            friday = 1
        if (weekday == "5"):
            saturday = 1
        if (weekday == "6"):
            sunday = 1
        if (weather == "Clear"):
            clear = 1
        if (weather == "Clouds"):
            clouds = 1
        if (weather == "Drizzle"):
            drizzle = 1
        if (weather == "Rain"):
            rain = 1
        if (weather == "Mist"):
            mist = 1
        weatherwithweekdy=[friday, monday, saturday, sunday, thursday, tuesday, wednesday, clear, clouds, drizzle, mist, rain]
        return (weatherwithweekdy)

    for weatherdata in weatherdatalists:
        if(len(weatherdata)==8):#both pickup and dropoff station
            stationNum_start = int(post[0])
            inputtime_start = datetime.strptime(weatherdata[0], '%Y-%m-%d %H:%M:%S')
            timeall.append(inputtime_start)
            weekday_start = inputtime_start.weekday()
            hour_start = int(inputtime_start.hour)
            stationNum_end = int(post[2])
            inputtime_end = datetime.strptime(weatherdata[4], '%Y-%m-%d %H:%M:%S')
            timeall.append(inputtime_end)
            weekday_end = inputtime_end.weekday()
            hour_end = int(inputtime_end.hour)
            temp_start = float(weatherdata[1])
            weather_start = weatherdata[2]
            windSpeed_start = float(weatherdata[3])
            temp_end = float(weatherdata[5])
            weather_end = weatherdata[6]
            windSpeed_end = float(weatherdata[7])
            datalist_start = weekday_weather(weekday_start,weather_start)
            datalist_end = weekday_weather(weekday_end,weather_end)


            #starting station
            predict_request = [[stationNum_start,temp_start,windSpeed_start,hour_start,datalist_start[0],datalist_start[1],datalist_start[2],datalist_start[3],datalist_start[4],datalist_start[5],datalist_start[6],datalist_start[7],datalist_start[8],datalist_start[9],datalist_start[10],datalist_start[11]]]
            available_bikes_P = random_forest_bikes.predict(predict_request)
            available_bikes_P = [int(available_bikes_P)]
            result.extend(available_bikes_P)
            #destination
            predict_request = [[stationNum_end,temp_end,windSpeed_end,hour_end,datalist_end[0],datalist_end[1],datalist_end[2],datalist_end[3],datalist_end[4],datalist_end[5],datalist_end[6],datalist_end[7],datalist_end[8],datalist_end[9],datalist_end[10],datalist_end[11]]]
            available_stands_P = random_forest_stands.predict(predict_request)
            available_stands_P = [int(available_stands_P)]
            result.extend(available_stands_P)

        elif(len(weatherdata)==4):#only pickup or dropoff station
            stationNum = int(post[0])
            inputtime= datetime.strptime(weatherdata[0], '%Y-%m-%d %H:%M:%S')
            timeall.append(inputtime)
            weekday = inputtime.weekday()
            hour = int(inputtime.hour)
            temp = float(weatherdata[1])
            weather = weatherdata[2]
            windSpeed= float(weatherdata[3])
            datalist = weekday_weather(weekday, weather)
            if(droptime == ''):
                # starting station
                predict_request = [
                    [stationNum, temp, windSpeed, hour, datalist[0], datalist[1], datalist[2],
                     datalist[3], datalist[4], datalist[5], datalist[6], datalist[7], datalist[8], datalist[9],
                     datalist[10], datalist[11]]]
                available_bikes_P = random_forest_bikes.predict(predict_request)
                available_bikes_P = [int(available_bikes_P)]
                result.extend(available_bikes_P)
            elif(picktime == ''):
                # destination
                predict_request = [
                    [stationNum, temp, windSpeed, hour, datalist[0], datalist[1], datalist[2],
                     datalist[3], datalist[4], datalist[5], datalist[6], datalist[7], datalist[8], datalist[9],
                     datalist[10], datalist[11]]]
                available_stands_P = random_forest_stands.predict(predict_request)
                available_stands_P = [int(available_stands_P)]
                result.extend(available_stands_P)

    finallist=[]
    if len(result)==5:
        if(droptime == ''):#only pickup station
            for i in range(len(timeall)):
                convertedtime = int(datetime.timestamp(timeall[i])*1000)
                resultlist.append([convertedtime,result[i]])
            finallist.append(resultlist)
            finallist.append([])
            finallist.append(selectedweather)
        elif (picktime == ''):#only dropoff station
            for i in range(len(timeall)):
                convertedtime = int(datetime.timestamp(timeall[i])*1000)
                resultlist.append([convertedtime,result[i]])
            finallist.append([])
            finallist.append(resultlist)
            finallist.append(selectedweather)
    elif len(result)==10:
        pickuplist = []
        dropofflist = []
        for i in range(len(timeall)):
            convertedtime = int(datetime.timestamp(timeall[i]) * 1000)
            resultlist.append([convertedtime, result[i]])
        for i in range(len(timeall)):
            if i%2 == 0:
                pickuplist.append(resultlist[i])
            else:
                dropofflist.append(resultlist[i])
        finallist.append(pickuplist)
        finallist.append(dropofflist)
        finallist.append(selectedweather)
    #print(finallist)
    return jsonify(preresult=finallist)

if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
