from flask import Flask
from flask import render_template
from datetime import datetime as dt
import string
import random
import json


app = Flask(__name__)

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

@app.route("/sharsies")
def sharsies():
    return
    


if __name__ == "__main__":
    app.run()