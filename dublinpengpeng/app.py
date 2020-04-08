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
    return render_template("homepage.html")

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
    DynamicInfo = "SELECT * FROM availability order by datetime desc limit 109;"
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

@app.route("/forcast", methods=['GET','POST'])
def prediction_model():
    """
    this part is to get the predicted data
    :return:
    """
    #get the data from the front end
    pick = request.form.get("pick")
    pickdate = request.form.get("pickdate")
    picktime = request.form.get("picktime")
    drop = request.form.get("drop")
    dropdate = request.form.get("dropdate")
    droptime = request.form.get("droptime")
    print("picktime: ",picktime)
    print("droptime: ", droptime)
    if picktime == '':
        print("end only")
        post = [drop,dropdate+" "+droptime]
    elif droptime == '':
        print("start only")
        post =  [pick,pickdate+" "+picktime]
    elif picktime != '' and droptime != '':
        print("both 2 stations")
        post = [pick, pickdate + " " + picktime, drop, dropdate + " " + droptime]
    print("post1:",post)

    def allweatherdata():
        url = 'http://api.openweathermap.org/data/2.5/forecast?q=Dublin,ie&units=metric&APPID=7c4d32959a99216eeb3c99efc8000278'  # 目前这个url可用
        weatherDataString = requests.get(url=url)
        allweather = weatherDataString.json()
        return allweather

    def weatherdata(post,pick,pickdate, picktime,drop,dropdate,droptime):
        allweather = allweatherdata()
        weatherdatalists = []
        if(len(post)==2):
            inputtime = datetime.strptime(post[1], '%Y-%m-%d %H:%M') - timedelta(hours=3)
            for k in range(6):
                weatherdatalist = []
                print(k)
                inputtime = inputtime + timedelta(hours=1)
                # print("inputtime: ",inputtime)
                three_hours_from_input = inputtime + timedelta(hours=1.5)
                three_hours_to_input = inputtime - timedelta(hours=1.5)
                for i in range(0, len(allweather['list'])):
                    time = allweather['list'][i]['dt_txt']
                    time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                    if (three_hours_from_input > time_datetime > three_hours_to_input):  # 目前只能做相等 还要改为大于小于
                        print("only start or end：",i,time)
                        temp = allweather['list'][i]['main']['temp']
                        cloud = allweather['list'][i]['weather'][0]['main']
                        speed = allweather['list'][i]['wind']['speed']
                        weatherdatalist.extend((str(inputtime),temp,cloud,speed))
                weatherdatalists.append(weatherdatalist)
                # print("加s:",weatherdatalists)
            return weatherdatalists
        elif(len(post)==4):
            inputtime_start = datetime.strptime(post[1], '%Y-%m-%d %H:%M') - timedelta(hours=3)
            print("post[3] is : ",post[3])
            inputtime_end = datetime.strptime(post[3], '%Y-%m-%d %H:%M') - timedelta(hours=3)
            for k in range(6):
                weatherdatalist = []
                inputtime_start = inputtime_start+ timedelta(hours=1)
                inputtime_end = inputtime_end + timedelta(hours=1)
                three_hours_from_start = inputtime_start + timedelta(hours=1.5)
                three_hours_to_start = inputtime_start - timedelta(hours=1.5)
                three_hours_from_end = inputtime_end + timedelta(hours=1.5)
                three_hours_to_end = inputtime_end - timedelta(hours=1.5)

                for i in range(0, len(allweather['list'])):
                    time = allweather['list'][i]['dt_txt']
                    time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                    if (three_hours_from_start > time_datetime > three_hours_to_start):
                        print("start:", i, time)
                        temp = allweather['list'][i]['main']['temp']
                        cloud = allweather['list'][i]['weather'][0]['main']
                        speed = allweather['list'][i]['wind']['speed']
                        weatherdatalist.extend((str(inputtime_start),temp, cloud, speed))
                        print("无s——start",weatherdatalist)
                for i in range(0, len(allweather['list'])):
                    time = allweather['list'][i]['dt_txt']
                    time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                    if (three_hours_from_end > time_datetime > three_hours_to_end):
                        print("end",i, time)
                        temp = allweather['list'][i]['main']['temp']
                        cloud = allweather['list'][i]['weather'][0]['main']
                        speed = allweather['list'][i]['wind']['speed']
                        weatherdatalist.extend((str(inputtime_end),temp, cloud, speed))
                        print("无s——end",weatherdatalist)
                weatherdatalists.append(weatherdatalist)
                print("加s:",weatherdatalists)
            return weatherdatalists

    weatherdatalists = weatherdata(post,pick,pickdate, picktime,drop,dropdate,droptime)
    print("final check weatherdatalists：",weatherdatalists)

    #以下第二部分：预测数据
    random_forest_bikes = pickle.load(open('final_prediction_bike.pickle', 'rb'))
    random_forest_stands = pickle.load(open("final_prediction_bike_stands.pickle", "rb"))
    # post.extend(weatherdatalists)
    result = []
    resultlist = [] #用来存放最后的 datetime+ bike/stands的list
    timeall=[]

    print("post:",post)

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
    #
    for weatherdata in weatherdatalists:
        # print(weatherdata)
        if(len(weatherdata)==8):#起始站都有
            print("enter this-2 station:")
            stationNum_start = int(post[0])
            inputtime_start = datetime.strptime(weatherdata[0], '%Y-%m-%d %H:%M:%S')
            timeall.append(inputtime_start)
            weekday_start = inputtime_start.weekday()
            hour_start = int(inputtime_start.hour)
            stationNum_end = int(post[2])
            inputtime_end = datetime.strptime(weatherdata[4], '%Y-%m-%d %H:%M:%S')
            timeall.append(inputtime_end)
            # print(timeall)
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

        elif(len(weatherdata)==4):#只有开始或结束
            print("enter this-1 station:")
            stationNum = int(post[0])
            inputtime= datetime.strptime(weatherdata[0], '%Y-%m-%d %H:%M:%S')
            timeall.append(inputtime)
            weekday = inputtime.weekday()
            hour = int(inputtime.hour)
            temp = float(weatherdata[1])
            weather = weatherdata[2]
            windSpeed= float(weatherdata[3])
            datalist = weekday_weather(weekday, weather)
            if(pick != None):
                # starting station
                predict_request = [
                    [stationNum, temp, windSpeed, hour, datalist[0], datalist[1], datalist[2],
                     datalist[3], datalist[4], datalist[5], datalist[6], datalist[7], datalist[8], datalist[9],
                     datalist[10], datalist[11]]]
                available_bikes_P = random_forest_bikes.predict(predict_request)
                available_bikes_P = [int(available_bikes_P)]
                result.extend(available_bikes_P)
            elif(drop != None):
                # destination
                predict_request = [
                    [stationNum, temp, windSpeed, hour, datalist[0], datalist[1], datalist[2],
                     datalist[3], datalist[4], datalist[5], datalist[6], datalist[7], datalist[8], datalist[9],
                     datalist[10], datalist[11]]]
                available_stands_P = random_forest_stands.predict(predict_request)
                available_stands_P = [int(available_stands_P)]
                result.extend(available_stands_P)

    print("所有时间: ", timeall)
    print("all bike/stands: ",result)
    for i in range(len(timeall)):
        convertedtime = int(datetime.timestamp(timeall[i])*1000)
        resultlist.append([convertedtime,result[i]])

    print(resultlist)

    return jsonify(preresult=resultlist)



if __name__ == '__main__':
    app.run(host="localhost", debug=True)