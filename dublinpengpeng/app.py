'''environment variable setting in terminal:

export FLASK_APP = flaskapp.py
flask run
export FLASK_DEBUG = 1 (set flask to debug mode)
'''

from flask import Flask, render_template, jsonify
import pymysql

app = Flask(__name__,static_url_path='')

def connect_to_database():
    conn = pymysql.connect(host='dublinbike.cczltqdfsp1t.eu-west-1.rds.amazonaws.com', user='root', passwd='shuyuqian',db='dublin')
    return conn


weatherQuery = "SELECT * FROM Weather WHERE dateTime=(SELECT MAX(dateTime) FROM Weather);"
DynamicInfo = "select * from availability order by datetime desc limit 110;"

@app.route("/")
def index():
    conn = connect_to_database()
    cursorObject = conn.cursor(pymysql.cursors.DictCursor)
    with cursorObject as cursor:
        cursor.execute(weatherQuery)
        wds = cursor.fetchall()
        cursor.execute(DynamicInfo)
        dbi = cursor.fetchall()
        dbi_items=[]
        for item in dbi:
            dbi_all=[]
            dbi_all.append(item['number'])
            dbi_all.append(item['available_bikes'])
            dbi_items.append(dbi_all)
        conn.close()
    # print(dbi_all);
    print(dbi_items);
    length=len(dbi_items);
    # print(item);
    return render_template('index.html', dbi=dbi_items, wds=wds,length_bike=length)

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
