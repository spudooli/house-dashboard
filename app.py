from flask import Flask, Response, jsonify
from flask import render_template
from datetime import datetime as dt
from datetime import datetime
from datetime import date
import pytz
import uuid
import urllib.request
import json
from flask_mysqldb import MySQL
import config
import socket
import paho.mqtt.client as paho
import redis
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

r = redis.StrictRedis('localhost', 6379, encoding="utf-8", decode_responses=True)

mysql = MySQL()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'bobthefish'
app.config['MYSQL_DB'] = 'spudooli'

mysql = MySQL(app)


def suffix(d):
    # Function to make the data human friendly
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    #Function to make the data human friendly
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def months_until_retirement():
    # Current date
    now = datetime.now()
    target_date = datetime(2032, 11, 17)
    difference = relativedelta(target_date, now)
    total_months = difference.years * 12 + difference.months
    return total_months

def format_time_with_am_pm(time_str):
    # Parse the input string to a datetime object
    dt = datetime.fromisoformat(time_str)
    
    # Format the datetime object to a string with AM/PM
    formatted_time = dt.strftime('%I:%M %p')
    
    return formatted_time


@app.route("/")
def dashboard():
    return render_template('index.html', title='Spudooli Dashboard')

@app.route("/indoortemperature")
def indoorTemperature():
    indoortemp = r.get('indoorTemperature')
    return indoortemp

@app.route("/power")
def power():
    power = r.get('power')
    #power = "{:,}".format(power)
    return power

@app.route("/bankbalance")
def bankbalance():
    html = "$" + r.get('bankbalance').split(".")[0]
    return html

@app.route("/bankbalancehistory")
def bankbalancehistory():
    # get the last 75 rows of the bank balance
    cursor = mysql.connection.cursor()
    cursor.execute("select amount, date from (SELECT * FROM bankbalance ORDER BY id DESC LIMIT 75)var1 order by date ASC")
    last75rows = cursor.fetchall()
    cursor.close()
    rows = []  
    for row in last75rows:
        rows.append(str(row[0]))
    return ','.join(rows)

@app.route("/outdoortemperature")
def outdoorTemperature():
    outdoortemp = r.get('outdoorTemperature')
    return outdoortemp

@app.route("/outsidehighslows")
def outsidehighslows():
    outdoorHigh = r.get("outdoorHigh") + "&deg;"
    outdoorLow = r.get("outdoorLow") + "&deg;"
    html = "<i class='material-icons' style='vertical-align:middle'>arrow_upward</i>" + outdoorHigh + "  <i class='material-icons' style='vertical-align:middle'>arrow_downward</i>" + outdoorLow
    return html

@app.route("/insidehighslows")
def insidehighslows():
    indoorHigh = r.get("indoorHigh") + "&deg;"
    indoorLow = r.get("indoorLow") + "&deg;"
    html = "<i class='material-icons' style='vertical-align:middle'>arrow_upward</i>" + indoorHigh + "  <i class='material-icons' style='vertical-align:middle'>arrow_downward</i>" + indoorLow
    return html

@app.route("/gettime")
def gettime():
    gettime = dt.now().strftime("%-I:%M%p")
    return gettime

@app.route("/getdate")
def getdate():
    getdate = custom_strftime('%A the {S}', dt.now())
    return getdate

@app.route("/hotwatercylinder")
def hotwater():
    hotwater = r.get('hotwater')
    if int(hotwater) == 0:
        html = "" 
    else:
        html =  "The hot water cylinder is heating"
    return html

@app.route("/spapoolheating")
def spapoolheating():
    jsonFile = open("/var/www/scripts/spa-operations.json", "r")
    data2 = json.load(jsonFile)
    jsonFile.close()
    spaHeating = data2["Heating"]
    if spaHeating == 1:
        html = "The spa is heating"
    else:
        html = ""   
    return html

@app.route("/the100x60project")
def the100x60project():
    the100x60project = int(r.get('total100x60'))
    the100x60project = "$" + f'{the100x60project:,}'
    return the100x60project

@app.route("/the100x60weeks")
def the100x60weeks():
    totalsavings = int(r.get('totalsavings'))
    return jsonify({
        'total_savings': totalsavings,
        'retirement_months': months_until_retirement(),
    })

@app.route("/rainradar")
def rainradar():
    rainradar = "<img src='/static/radar.gif?v=" + str(uuid.uuid4()) + "' height='300' width='300' align=left>"
    return rainradar

@app.route("/isobars")
def isobars():
    isobars = "<img src='/static/isobars/isobars_loop.gif?v=" + str(uuid.uuid4()) + "' width='400' align='left'>"
    return isobars

@app.route("/thesun")
def thesun():
    return jsonify({
        'sunrise': format_time_with_am_pm(r.get('sunrise')),
        'sunset': format_time_with_am_pm(r.get('sunset')),
    })

@app.route("/simplicity")
def simplicity():
    homeloanbalance = r.get('homeloanbalance')
    punakaikicurrentvalue = 11336
    homeloanmonths = int(homeloanbalance.split(".")[0].replace("-", "").replace(",", "")) / 4000
    homeloanTarget = date.today() + relativedelta(months=+int(homeloanmonths))

    sharesiesbalance = int(r.get('sharesies'))
    dave_int = int(r.get("simplicityDave").replace(",", "").replace("$", "").replace(".", ""))
    gabba_int = int(r.get("simplicityGabba").replace(",", "").replace("$", "").replace(".", ""))
    totalsavings = dave_int + gabba_int + punakaikicurrentvalue + sharesiesbalance
    the100x60projectbalance = punakaikicurrentvalue + sharesiesbalance

    broker = "192.168.1.2"
    port = 1883
    client1 = paho.Client(paho.CallbackAPIVersion.VERSION2, "dashboardthe100x60project")
    client1.connect(broker, port)

    def on_connect(client, userdata, flags, reason_code, properties):
        print("Connected With Result Code " + str(reason_code))

    client1.on_connect = on_connect
    client1.publish("house/money/total100x60", the100x60projectbalance)
    client1.publish("house/money/totalsavings", totalsavings)
    client1.disconnect()

    return jsonify({
        'homeloan': homeloanbalance.split(".")[0],
        'homeloan_end': homeloanTarget.strftime("%b %Y"),
        'kiwisaver_dave': dave_int,
        'kiwisaver_gabba': gabba_int,
        'punakaiki': punakaikicurrentvalue,
        'retirement_months': months_until_retirement(),
    })

@app.route("/sharesies")
def sharesies():
    sharesiesbalance = int(r.get('sharesies'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, amount FROM `sharesies` order by`id` DESC limit 1")
    yesterdaysbalance = cursor.fetchone()
    change = sharesiesbalance - yesterdaysbalance[1]
    cursor.close()
    r.set('sharesieschange', int(change))
    return jsonify({
        'balance': sharesiesbalance,
        'change': int(change),
    })

@app.route("/websitecomments")
def websitecomments():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT count(id) count FROM `pixelpost_comments` where publish = 'no'")
    websitecomments = cursor.fetchone()
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT count(id) count FROM `contactus` where checked is NULL")
    contactus = cursor.fetchone()
    cursor.close()
    if websitecomments[0] > 0 or contactus[0] > 0:
        html = str(websitecomments[0]) + " comments/contactus awaiting approval"
    else:
        html = ""
    return html

@app.route("/gardenlights")
def gardenlights():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('192.168.1.147', 80))
    if result == 0:
        html = ""
    else:
        html = "<i class='material-icons' style='font-size:20px;color:red'>error</i> Garden Lights"
    return html 

@app.route("/verandahlights")
def verandahlights():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('192.168.1.150', 80))
    if result == 0:
        html = ""
    else:
        html = "<i class='material-icons' style='font-size:20px;color:red'>error</i> Verandah Lights"
    return html 

@app.route("/gardenshed")
def gardenshed():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('192.168.1.150', 80))
    if result == 0:
        html = ""
    else:
        #html = ""
        html = "<i class='material-icons' style='font-size:20px;color:red'>error</i> Garden Shed"
    return html 

@app.route("/spapooltemperature")
def spapooltemperature():
    waterTemp = r.get('spatemperature')
    if waterTemp == 0:
        waterTemp = "-"
    html = "Spa Pool: " + str(waterTemp) + "&deg;C"
    return html 

@app.route("/osmc")
def osmc():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('192.168.1.65', 22))
    if result == 0:
        html = ""
    else:
        html = "<i class='material-icons' style='font-size:20px;color:red'>error</i> OSMC"
    return html 

@app.route("/davelocation")
def davelocation():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM `track` where who = 3 ORDER BY `id` DESC limit 1")
    davelocation = cursor.fetchone()
    cursor.close()
    daveupdated = str(davelocation[1])
    html = "<img src='/static/location/dave_map_" + str(davelocation[8]) + ".png' class='mapgrayscale'><p class='stat_measure' id='current_date' >Updated:" + daveupdated + "</p>"
    return html
    
@app.route("/gabbalocation")
def gabbalocation():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM `track` where who = 4 ORDER BY `id` DESC limit 1")
    gabbalocation = cursor.fetchone()
    cursor.close()
    gabbaupdated = str(gabbalocation[1])
    html = "<img src='/static/location/gabba_map_" + str(gabbalocation[8]) + ".png' class='mapgrayscale'><p class='stat_measure' id='current_date' >Updated:" + gabbaupdated + "</p>"
    return html

@app.route("/location-stream")
def location_stream():
    def event_stream():
        pubsub = r.pubsub()
        pubsub.subscribe('location:dave', 'location:gabba')
        try:
            while True:
                msg = pubsub.get_message(timeout=30)
                if msg and msg['type'] == 'message':
                    channel = msg['channel']
                    who = 'dave' if channel == 'location:dave' else 'gabba'
                    yield f"data: {json.dumps({'who': who})}\n\n"
                else:
                    yield ": keepalive\n\n"
        except GeneratorExit:
            pubsub.unsubscribe()
            pubsub.close()
    return Response(event_stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route("/weather")
def weather():
    indoorPressure = r.get("indoorPressure")
    return jsonify({
        'today': {
            'forecast': r.get("todayForecast"),
            'max': r.get("todayMax"),
            'min': r.get("todayMin"),
        },
        'tomorrow': {
            'forecast': r.get("tomorrowForecast"),
            'max': r.get("tomorrowMax"),
            'min': r.get("tomorrowMin"),
        },
        'saturday': r.get("saturdayCondition"),
        'sunday': r.get("sundayCondition"),
        'pressure': {
            'value': indoorPressure[0:-2],
            'direction': r.get("pressureDirection"),
        },
    })

if __name__ == "__main__":
    app.run()
