from flask import Flask
from flask import render_template
from datetime import datetime as dt
import string
import random
import urllib.request
import json
from flask_mysqldb import MySQL
import config


app = Flask(__name__)


mysql = MySQL()

app.config['MYSQL_HOST'] = '192.168.1.2'
app.config['MYSQL_USER'] = 'sammy'
app.config['MYSQL_PASSWORD'] = 'bobthefish'
app.config['MYSQL_DB'] = 'spudooli'

mysql = MySQL(app)


def statusFile(thing):
    jsonFile = open("/var/www/scripts/statusfile.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()
    return data[thing]

def suffix(d):
    # Function to make the data human friendly
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    #Function to make the data human friendly
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


@app.route("/")
def dashboard():
    return render_template('index.html', title='Spudooli Dashboard')

@app.route("/indoortemperature")
def indoorTemperature():
    indoortemp = statusFile("indoorTemperature") + "&deg;"
    return indoortemp

@app.route("/bankbalance")
def bankbalance():
    f = open("/var/www/scripts/otherbalance.txt", "r")    
    bankbalance = f.read()
    html = "$" + bankbalance.split(".")[0]
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
        rows.append(row[0])
    print(rows)
    html = "html"
    return html

@app.route("/outdoortemperature")
def outdoorTemperature():
    outdoortemp = statusFile("outdoorTemperature") + "&deg;"
    return outdoortemp

@app.route("/outsidehighslows")
def outsidehighslows():
    outdoorHigh = statusFile("outdoorHigh") + "&deg;"
    outdoorLow = statusFile("outdoorLow") + "&deg;"
    html = "Today's High: " +  outdoorHigh + "<br />  Todays Low: " + outdoorLow + "</p>"
    return html

@app.route("/insidehighslows")
def insidehighslows():
    indoorHigh = statusFile("indoorHigh") + "&deg;"
    indoorLow = statusFile("indoorLow") + "&deg;"
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

@app.route("/the100x60project")
def the100x60project():
    the100x60project = int(statusFile("total100x60").split(".")[0])
    the100x60project = "$" + f'{the100x60project:,}'
    return the100x60project

@app.route("/rainradar")
def rainradar():
    letters = string.ascii_lowercase
    rainradar = "<img src='https://www.spudooli.com/dashboard/radar.gif?v=" + ''.join(random.choice(letters) for i in range(10)) + "' height='300' width='300' align=left>"
    return rainradar

@app.route("/isobars")
def isobars():
    letters = string.ascii_lowercase
    isobars = "<img src='https://www.spudooli.com/dashboard/isobars.jpeg?v=" + ''.join(random.choice(letters) for i in range(10)) + "' width='400' align='left'>"
    return isobars

@app.route("/thesun")
def thesun():
    sunrise = statusFile("sunrise")
    sunset = statusFile("sunset")
    html = "<span><strong>The Sun: </strong> " + sunrise + " and " + sunset
    return html

@app.route("/simplicity")
def simplicity():
    simplicityDave = statusFile("simplicityDave")
    simplicityGabba = statusFile("simplicityGabba")
    homeloanbalance = statusFile("homeloanbalance")
    punakaikicurrentvalue = "$8,122"
    html = "<strong>Home Loan:</strong> " +  homeloanbalance + "<br><br><strong>Kiwisaver Dave:</strong> " + simplicityDave + "<br><strong>Kiwisaver Gabba:</strong> " + simplicityGabba + "<br><strong>Punakaiki:</strong> " + punakaikicurrentvalue
    return html

@app.route("/sharesies")
def sharesies():
    f = open("/var/www/scripts/sharesiesbalance.txt", "r")    
    sharesiesbalance = f.read()
    html = "Sharesies: $" + sharesiesbalance.split(".")[0]
    return html

@app.route("/davelocation")
def davelocation():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM `track` where who = 3 ORDER BY `id` DESC limit 1")
    davelocation = cursor.fetchone()
    print(davelocation)
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
    print(gabbalocation)
    cursor.close()
    gabbaupdated = str(gabbalocation[1])
    gabbalatlon = str(gabbalocation[3]) + "," + str(gabbalocation[4])
    html = "<img src='https://maps.googleapis.com/maps/api/staticmap?center=" + gabbalatlon + "&zoom=15&size=350x300&markers=color:0xD0E700%7Clabel:G%7C" + gabbalatlon + "&sensor=false&key=" + config.googlemapsapikey + "&visual_refresh=true&maptype=terrain'><p class='stat_measure' id='current_date' >Updated:" + gabbaupdated + "</p>"
    return html

@app.route("/weather")
def weather():
    thesunurl = "http://metservice.com/publicData/localForecastauckland"
    openUrl = urllib.request.urlopen(thesunurl)
    data = openUrl.read()
    jsonData = json.loads(data)

    todayforecast = jsonData['days'][0]['forecast']
    #todayforecastword = jsonData['days'][0]['forecastWord']
    todaymax = jsonData['days'][0]['max']
    todaymin = jsonData['days'][0]['min']

    tomorrowforecast = jsonData['days'][1]['forecast']
    #tomorrowforecastword = jsonData['days'][1]['forecastWord']
    tomorrowmax = jsonData['days'][1]['max']
    tomorrowmin = jsonData['days'][1]['min']

    saturday = jsonData['saturdayForecastWord']
    sunday = jsonData['sundayForecastWord']

    if saturday == "Partly cloudy":
        saturdayicon = "<span class='fs1 climacon cloud sun' aria-hidden='true'></span>"
    if saturday == "Few showers":
        saturdayicon = "<span class='fs1 climacon showers sun' aria-hidden='true'></span>"
    if saturday == "Showers":
        saturdayicon = "<span class='fs1 climacon shoers' aria-hidden='true'></span>"
    if saturday == "Rain":
        saturdayicon = "<span class='fs1 climacon rain' aria-hidden='true'></span>"
    if saturday == "Fine":
        saturdayicon = "<span class='fs1 climacon sun' aria-hidden='true'></span>"
    if saturday == "Cloudy":
        saturdayicon = "<span class='fs1 climacon cloud' aria-hidden='true'></span>"
    if saturday == "Wind rain":
        saturdayicon = "<span class='fs1 climacon wind cloud' aria-hidden='true'></span>"
    if saturday == "Drizzle":
        saturdayicon = "<span class='fs1 climacon drizzle' aria-hidden='true'></span>"
    if saturday == "Windy":
        saturdayicon = "<span class='fs1 climacon wind' aria-hidden='true'></span>"
    if saturday == "Thunder":
        saturdayicon = "<span class='fs1 climacon thunder' aria-hidden='true'></span>"

    if sunday == "Partly cloudy":
        sundayicon = "<span class='fs1 climacon cloud sun' aria-hidden='true'></span>"
    if sunday == "Few showers":
        sundayicon = "<span class='fs1 climacon showers sun' aria-hidden='true'></span>"
    if sunday == "Showers":
        sundayicon = "<span class='fs1 climacon shoers' aria-hidden='true'></span>"
    if sunday == "Rain":
        sundayicon = "<span class='fs1 climacon rain' aria-hidden='true'></span>"
    if sunday == "Fine":
        sundayicon = "<span class='fs1 climacon sun' aria-hidden='true'></span>"
    if sunday == "Cloudy":
        sundayicon = "<span class='fs1 climacon cloud' aria-hidden='true'></span>"
    if sunday == "Wind rain":
        sundayicon = "<span class='fs1 climacon wind cloud' aria-hidden='true'></span>"
    if sunday == "Drizzle":
        sundayicon = "<span class='fs1 climacon drizzle' aria-hidden='true'></span>"
    if sunday == "Windy":
        sundayicon = "<span class='fs1 climacon wind' aria-hidden='true'></span>"
    if sunday == "Thunder":
        sundayicon = "<span class='fs1 climacon thunder' aria-hidden='true'></span>"

    #pressuredirection = statusFile("pressureDirection")
    pressuredirection = "upslowly"
    if pressuredirection == "upslowly":
        pressuredirectionicon= "<i class='material-icons' >arrow_upward</i>"
    if pressuredirection == "upslowly-goodcoming":
        pressuredirectionicon= "<i class='material-icons' >arrow_upward</i>"
    if pressuredirection == "downslowly":
        pressuredirectionicon= "<i class='material-icons' >arrow_downward</i>"
    if pressuredirection == "downslowly-nogoodcoming":
        pressuredirectionicon= "<i class='material-icons' >arrow_downward</i>"
    if pressuredirection == "stable":
        pressuredirectionicon= "<i class='material-icons' >arrow_forward</i>"

    #indoorPressure = statusFile("indoorPressure")
    indoorPressure = "1000"

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