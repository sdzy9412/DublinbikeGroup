'''environment variable setting in terminal:

export FLASK_APP = flaskapp.py
flask run
export FLASK_DEBUG = 1 (set flask to debug mode)
'''

from flask import Flask, g, render_template, jsonify
from flask import session, redirect, url_for
import pymysql
from sqlalchemy import create_engine

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, EqualTo

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
            return render_template("login.html", message = "Successfully Logged In!")
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
    sql = "SELECT * FROM availability where number = {} order by datetime desc;".format(station_id)
    rows = engine.execute(sql)
    for row in rows:
        availableid.append(dict(row))

    return jsonify(availableid = availableid)

if __name__ == '__main__':
    app.run(host="localhost", debug=True)