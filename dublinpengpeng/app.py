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

@app.route("/predict", methods=["POST"])
def send():
    pick = request.form.get("pick")
    pickdate = request.form.get("pickdate")
    picktime = request.form.get("picktime")
    drop = request.form.get("drop")
    dropdate = request.form.get("dropdate")
    droptime = request.form.get("droptime")
    return render_template("submit.html", pick=pick, drop=drop, pickdate=pickdate, picktime=picktime, dropdate=dropdate, droptime=droptime)

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
            return render_template("homepage.html")
    return render_template("login.html", form = form)

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('root'))

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

@app.route("/prediction_model", methods=['GET','POST'])
def prediction_model():
    #通过post得到所要的数据(如果是分开传？)
    #第一部分：得到对应时间的预测天气
    # post = request.args.get('id', 0, type=str) #如果是一起传过来的
    # 或者：post = str(request.args.get('id', 0, type=str)) #post来的时间
    # post = post.split() #如果split后把日期与时间分开 我再post[1]=post[1]+post[2]应该就可以
    post = [42, "2020-04-08 02:00:00", 0]  # 只是测试 实际代码为下下一行
    post = [42,"2020-04-08 02:00:00",0,31,"2020-04-08 09:00:00",1] # 只是测试 实际代码为下一行
    def allweatherdata():
        url = 'http://api.openweathermap.org/data/2.5/forecast?q=Dublin,ie&units=metric&APPID=7c4d32959a99216eeb3c99efc8000278'  # 目前这个url可用
        weatherDataString = requests.get(url=url)
        allweather = weatherDataString.json()
        return allweather

    def weatherdata(post):
        allweather = allweatherdata()
        weatherdatalist = []
        if(len(post)==3):
            inputtime = datetime.strptime(post[1], '%Y-%m-%d %H:%M:%S')
            three_hours_from_input = inputtime + timedelta(hours=3)
            three_hours_to_input = inputtime - timedelta(hours=3)
            print(three_hours_from_input)
            print(three_hours_to_input)
            print("以上是输入时间加减3小时")
            for i in range(0, len(allweather['list'])):
                time = allweather['list'][i]['dt_txt']
                time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                # type(time)
                if (three_hours_from_input > time_datetime > three_hours_to_input):  # 目前只能做相等 还要改为大于小于
                    print(i,time)
                    temp = allweather['list'][i]['main']['temp']
                    cloud = allweather['list'][i]['weather'][0]['main']
                    speed = allweather['list'][i]['wind']['speed']
                    weatherdatalist.extend((temp,cloud,speed))
                    return weatherdatalist
        elif(len(post)==6):
            inputtime_start = datetime.strptime(post[1], '%Y-%m-%d %H:%M:%S')
            inputtime_end = datetime.strptime(post[4], '%Y-%m-%d %H:%M:%S')
            three_hours_from_start = inputtime_start + timedelta(hours=1.5)
            three_hours_to_start = inputtime_start - timedelta(hours=1.5)
            three_hours_from_end = inputtime_end + timedelta(hours=1.5)
            three_hours_to_end = inputtime_end - timedelta(hours=1.5)

            for i in range(0, len(allweather['list'])):
                time = allweather['list'][i]['dt_txt']
                time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                # type(time)
                if (three_hours_from_start > time_datetime > three_hours_to_start):
                    print("start:", i, time)
                    temp = allweather['list'][i]['main']['temp']
                    cloud = allweather['list'][i]['weather'][0]['main']
                    speed = allweather['list'][i]['wind']['speed']
                    weatherdatalist.extend((temp, cloud, speed))
            for i in range(0, len(allweather['list'])):
                time = allweather['list'][i]['dt_txt']
                time_datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                # type(time)
                if (three_hours_from_end > time_datetime > three_hours_to_end):
                    print("end",i, time)
                    temp = allweather['list'][i]['main']['temp']
                    cloud = allweather['list'][i]['weather'][0]['main']
                    speed = allweather['list'][i]['wind']['speed']
                    weatherdatalist.extend((temp, cloud, speed))
            return weatherdatalist

    weatherdatalist = weatherdata(post)
    print(weatherdatalist)

    #以下第二部分：预测数据
    #传入信息格式：[num,time,0/1]
    # eg:只有起点[42,"2020-04-08 02:00:00",0] 只有终点同理将0改为1
    # 起点终点都有[42,"2020-04-08 02:00:00",0,31,"2020-04-08 09:00:00",1]
    random_forest_bikes = pickle.load(open('final_prediction_bike.pickle', 'rb'))
    random_forest_stands = pickle.load(open("final_prediction_bike_stands.pickle", "rb"))
    # post = request.args.get('id', 0, type=str)
    # post = post.split()
    post.extend(weatherdatalist)
    result = []
    #上一步的结果：0起点站 1开始时间 2标志1 3终点站 4结束时间 5标志2 6气温1 7天气1 8风速1 9气温2 10天气2 11风速2
    # post = [42, '2020-04-08 02:00:00', 0, 31, '2020-04-08 09:00:00', 1, 5.8, 'Clear', 3.56, 9.56, 'Clouds', 2.16]
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

    if(len(post)==12):
        print("enter this:")
        # post = [42, "2020-04-08 02:00:00", 0, 31, "2020-04-08 09:00:00", 1]
        stationNum_start = int(post[0])
        inputtime_start = datetime.strptime(post[1], '%Y-%m-%d %H:%M:%S')
        weekday_start = inputtime_start.weekday()
        hour_start = int(inputtime_start.hour)
        stationNum_end = int(post[3])
        inputtime_end = datetime.strptime(post[4], '%Y-%m-%d %H:%M:%S')
        weekday_end = inputtime_end.weekday()
        hour_end = int(inputtime_end.hour)
        temp_start = float(post[6])
        weather_start = post[7]
        windSpeed_start = float(post[8])
        temp_end = float(post[9])
        weather_end = post[10]
        windSpeed_end = float(post[11])
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
    # post = [42, '2020-04-08 02:00:00', 0, 5.8, 'Clear', 3.56]
    elif(len(post)==6):
        stationNum = int(post[0])
        inputtime= datetime.strptime(post[1], '%Y-%m-%d %H:%M:%S')
        weekday = inputtime.weekday()
        hour = int(inputtime.hour)
        flag = int(post[2])  #
        temp = float(post[3])
        weather = post[4]
        windSpeed= float(post[5])
        datalist = weekday_weather(weekday, weather)
        if(flag == 0):
            # starting station
            predict_request = [
                [stationNum, temp, windSpeed, hour, datalist[0], datalist[1], datalist[2],
                 datalist[3], datalist[4], datalist[5], datalist[6], datalist[7], datalist[8], datalist[9],
                 datalist[10], datalist[11]]]
            available_bikes_P = random_forest_bikes.predict(predict_request)
            available_bikes_P = [int(available_bikes_P)]
            result.extend(available_bikes_P)
        elif(flag==1):
            # destination
            predict_request = [
                [stationNum, temp, windSpeed, hour, datalist[0], datalist[1], datalist[2],
                 datalist[3], datalist[4], datalist[5], datalist[6], datalist[7], datalist[8], datalist[9],
                 datalist[10], datalist[11]]]
            available_stands_P = random_forest_stands.predict(predict_request)
            available_stands_P = [int(available_stands_P)]
            result.extend(available_stands_P)

    result.extend(weatherdatalist)
    return jsonify(result)



if __name__ == '__main__':
    app.run(host="localhost", debug=True)