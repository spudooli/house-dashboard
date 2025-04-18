from flask import Flask
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

r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

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
    indoortemp = r.get('indoorTemperature') + "&deg;"
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
    balancehistorylist = ','.join(rows)
    html = "<span class='bankbalancehistory'>" + balancehistorylist
    html += "</span><script type='text/javascript'>"
    html += "$(function() {"
    html += "$('.inlinesparkline').sparkline();"
    html += "$('.bankbalancehistory').sparkline('html', {type: 'bar', barColor: '#D0E700'} );"
    html += "});"
    html += "</script>"
    return html

@app.route("/outdoortemperature")
def outdoorTemperature():
    outdoortemp = r.get('outdoorTemperature')
    return outdoortemp

@app.route("/outsidehighslows")
def outsidehighslows():
    outdoorHigh = r.get("outdoorHigh") + "&deg;"
    outdoorLow = r.get("outdoorLow") + "&deg;"
    html = "Today's High: " +  outdoorHigh + "<br />  Today's Low: " + outdoorLow + "</p>"
    return html

@app.route("/insidehighslows")
def insidehighslows():
    indoorHigh = r.get("indoorHigh") + "&deg;"
    indoorLow = r.get("indoorLow") + "&deg;"
    html = "Today's High: " +  indoorHigh + "<br />  Todays Low: " + indoorLow + "</p>"
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
    # d1 = date.today()
    # d2 = date(2027,11,17)
    # weeks = (d2-d1).days//7
    # the100x60project = int(r.get('total100x60'))
    # averageperweektogo = int("100000") - int(the100x60project)
    # averageperweektogo = int(averageperweektogo) / weeks
    # averageperweektogo = str(averageperweektogo)
    totalsavings = int(r.get('totalsavings'))
    html = "<br>Total Retirement Savings: <strong>$" + "{:,}".format(totalsavings) + "</strong>"
    return html

@app.route("/rainradar")
def rainradar():
    rainradar = "<img src='/static/radar.gif?v=" + str(uuid.uuid4()) + "' height='300' width='300' align=left>"
    return rainradar

@app.route("/isobars")
def isobars():
    isobars = "<img src='/static/isobars.jpeg?v=" + str(uuid.uuid4()) + "' width='400' align='left'>"
    return isobars

@app.route("/thesun")
def thesun():

    sunrise = format_time_with_am_pm(r.get('sunrise'))
    sunset = format_time_with_am_pm(r.get('sunset'))
    html = "<span>The Sun: <strong>" + sunrise + "</strong>  and <strong>" + sunset + "</strong></span>"
    
    return html

@app.route("/simplicity")
def simplicity():
    simplicityDave = r.get("simplicityDave")
    simplicityGabba = r.get("simplicityGabba")
    homeloanbalance = r.get('homeloanbalance')
    punakaikicurrentvalue = "10811"
    homeloanmonths = homeloanbalance.split(".")[0].replace("-$", "").replace(",", "")
    homeloanmonths = int(homeloanmonths) / 4000
    homeloanTarget= date.today() + relativedelta(months=+int(homeloanmonths))

    html = "Home Loan:<strong> " +  homeloanbalance + "</strong><br>Forecast end date: <strong>" + homeloanTarget.strftime("%b %Y") + "</strong><br><br>Kiwisaver Dave:<strong> $" + "{:,}".format(int(simplicityDave)) + "<br></strong>Kiwisaver Gabba:<strong> $" + "{:,}".format(int(simplicityGabba)) + "<br></strong>Punakaiki:<strong> $" + "{:,}".format(int(punakaikicurrentvalue))  + "</strong> <br> Retiring in <strong>" + str(months_until_retirement()) + "</strong> months" 

    # Calculate the100x60project balance here only because I have most of the values needed already
    sharesiesbalance = int(r.get('sharesies'))
    simplicityDave = simplicityDave.replace(",", "").replace("$", "").replace(".", "")
    simplicityGabba = simplicityGabba.replace(",", "").replace("$", "").replace(".", "")
    totalsavings = int(simplicityDave) + int(simplicityGabba) + int(punakaikicurrentvalue) + int(sharesiesbalance) 
    #networth = int(totalsavings) + int(1000000) - int(homeloanbalance)
    the100x60projectbalance = int(punakaikicurrentvalue) + int(sharesiesbalance)

    broker = "192.168.1.2"
    port = 1883
    client1 = paho.Client("dashboardthe100x60project")
    client1.connect(broker, port)

    def on_connect(client, userdata, flags, rc):
        print("Connected With Result Code "+rc)

    client1.publish("house/money/total100x60", the100x60projectbalance)
    #client1.publish("house/money/networth", networth)
    client1.publish("house/money/totalsavings", totalsavings)
    client1.disconnect

    return html

@app.route("/sharesies")
def sharesies():
    sharesiesbalance = int(r.get('sharesies'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, amount FROM `sharesies` order by`id` DESC limit 1")
    yesterdaysbalance = cursor.fetchone()
    change = sharesiesbalance - yesterdaysbalance[1]
    cursor.close()
    r.set('sharesieschange', int(change))
    html = "Sharesies:<strong> $" + str("{:,}".format(sharesiesbalance)) + "</strong></br> Change today: $" + str(change).split(".")[0]
    return html

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

@app.route("/i3chargingstatus")
def i3chargingstatus():
    i3chargingstatus = r.get('i3chargingstatus')
    if i3chargingstatus == "CHARGING":
        charging = " CHARGING"
        i3chargecompletiontime = r.get('i3chargecompletiontime')
        # Convert the given datetime string to a datetime object
        dete = datetime.fromisoformat(i3chargecompletiontime)
        # Set the timezone to NZ
        nz_tz = pytz.timezone('Pacific/Auckland')
        dt_nz = dete.astimezone(nz_tz)
        # Print the NZ timezone time
        i3chargecompletiontime_formatted_time = dt_nz.strftime('%Y-%m-%d %H:%M')
        html = f"<strong>{r.get('i3batteryremaining')}% {charging} until  {i3chargecompletiontime_formatted_time}</strong>"
    else:
        charging = ""
        #html = f"Battery Remaining: <strong>{r.get('i3batteryremaining')}%</strong>"
        html = f"<div class='audienceGraph' id='audience_caffeination_percentage' style='width:{int(r.get('i3batteryremaining')) - 5}%;'><span class='audiencePercent caffeination_level_1'>{r.get('i3batteryremaining')}%</span>"

    return html

@app.route("/i3rangeremaining")
def i3rangeremaining():
    i3rangeremaining = f"{r.get('i3rangeremaining')}"
    return i3rangeremaining

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
    davelatlon = str(davelocation[3]) + "," + str(davelocation[4])
    html = "<img src='https://maps.googleapis.com/maps/api/staticmap?center=" + davelatlon + "&zoom=15&size=350x300&markers=color:0xD0E700%7Clabel:D%7C" + davelatlon + "&sensor=false&key=" + config.googlemapsapikey + "&visual_refresh=true&maptype=terrain'><p class='stat_measure' id='current_date' >Updated:" + daveupdated + "</p>"
    return html
    
@app.route("/gabbalocation")
def gabbalocation():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM `track` where who = 4 ORDER BY `id` DESC limit 1")
    gabbalocation = cursor.fetchone()
    cursor.close()
    gabbaupdated = str(gabbalocation[1])
    gabbalatlon = str(gabbalocation[3]) + "," + str(gabbalocation[4])
    html = "<img src='https://maps.googleapis.com/maps/api/staticmap?center=" + gabbalatlon + "&zoom=15&size=350x300&markers=color:0xD0E700%7Clabel:G%7C" + gabbalatlon + "&sensor=false&key=" + config.googlemapsapikey + "&visual_refresh=true&maptype=terrain'><p class='stat_measure' id='current_date' >Updated:" + gabbaupdated + "</p>"
    return html

@app.route("/weather")
def weather():

    todayforecast = r.get("todayForecast")
    todaymax = r.get("todayMax")
    todaymin = r.get("todayMin")

    tomorrowforecast = r.get("tomorrowForecast")
    tomorrowmax = r.get("tomorrowMax")
    tomorrowmin = r.get("tomorrowMin")

    saturday = r.get("saturdayCondition")
    print(saturday)
    sunday = r.get("sundayCondition")
    print(saturday)
   
    if saturday == "partly-cloudy":
        saturdayicon = "<span class='fs1 climacon cloud sun' aria-hidden='true'></span>"
    if saturday == "few-showers":
        saturdayicon = "<span class='fs1 climacon showers sun' aria-hidden='true'></span>"
    if saturday == "showers":
        saturdayicon = "<span class='fs1 climacon showers' aria-hidden='true'></span>"
    if saturday == "rain":
        saturdayicon = "<span class='fs1 climacon rain' aria-hidden='true'></span>"
    if saturday == "fine":
        saturdayicon = "<span class='fs1 climacon sun' aria-hidden='true'></span>"
    if saturday == "cloudy":
        saturdayicon = "<span class='fs1 climacon cloud' aria-hidden='true'></span>"
    if saturday == "wind-rain":
        saturdayicon = "<span class='fs1 climacon wind cloud' aria-hidden='true'></span>"
    if saturday == "drizzle":
        saturdayicon = "<span class='fs1 climacon drizzle' aria-hidden='true'></span>"
    if saturday == "windy":
        saturdayicon = "<span class='fs1 climacon wind' aria-hidden='true'></span>"
    if saturday == "thunder":
        saturdayicon = "<span class='fs1 climacon lightning' aria-hidden='true'></span>"

    if sunday == "partly-cloudy":
        sundayicon = "<span class='fs1 climacon cloud sun' aria-hidden='true'></span>"
    if sunday == "few-showers":
        sundayicon = "<span class='fs1 climacon showers sun' aria-hidden='true'></span>"
    if sunday == "showers":
        sundayicon = "<span class='fs1 climacon showers' aria-hidden='true'></span>"
    if sunday == "rain":
        sundayicon = "<span class='fs1 climacon rain' aria-hidden='true'></span>"
    if sunday == "fine":
        sundayicon = "<span class='fs1 climacon sun' aria-hidden='true'></span>"
    if sunday == "cloudy":
        sundayicon = "<span class='fs1 climacon cloud' aria-hidden='true'></span>"
    if sunday == "wind-rain":
        sundayicon = "<span class='fs1 climacon wind cloud' aria-hidden='true'></span>"
    if sunday == "drizzle":
        sundayicon = "<span class='fs1 climacon drizzle' aria-hidden='true'></span>"
    if sunday == "windy":
        sundayicon = "<span class='fs1 climacon wind' aria-hidden='true'></span>"
    if sunday == "thunder":
        sundayicon = "<span class='fs1 climacon lightning' aria-hidden='true'></span>"

    pressuredirection = r.get("pressureDirection")
    if pressuredirection == "up":
        pressuredirectionicon= "<i class='material-icons' >arrow_upward</i>"
    if pressuredirection == "upslowly":
        pressuredirectionicon= "<i class='material-icons' >arrow_upward</i>"
    if pressuredirection == "upslowly-goodcoming":
        pressuredirectionicon= "<i class='material-icons' >arrow_upward</i>"
    if pressuredirection == "downslowly":
        pressuredirectionicon= "<i class='material-icons' >arrow_downward</i>"
    if pressuredirection == "down":
        pressuredirectionicon= "<i class='material-icons' >arrow_downward</i>"
    if pressuredirection == "downslowly-nogoodcoming":
        pressuredirectionicon= "<i class='material-icons' >arrow_downward</i>"
    if pressuredirection == "stable":
        pressuredirectionicon= "<i class='material-icons' >arrow_forward</i>"


    indoorPressure = r.get("indoorPressure")
    indoorPressure = indoorPressure[0:-2]

    html = todayforecast + "<br>"
    html += "Max: " + todaymax + "&deg;  Min: " + todaymin + "&deg;<br><br>"
    html += "<strong>Tomorrow</strong> &nbsp; &nbsp; &nbsp; Max: " +  tomorrowmax + "&deg;  Min: " + tomorrowmin + "&deg;<br>"
    html +=  tomorrowforecast + "<br>"
    html += "<br><table width=100%><tr><th>Pressure</th><th>Saturday</th><th>Sunday</th></tr>"
    html += "<tr><td><h3>" + indoorPressure + pressuredirectionicon + "</h3></td>"
    html += "<td>" + saturdayicon + "</td>"
    html += "<td>" + sundayicon + "</td></tr></table>"

    return html

if __name__ == "__main__":
    app.run()
