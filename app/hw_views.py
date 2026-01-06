# Maythanan Ladee (Frame)
# 670510722
# sec001

import requests
import json
from datetime import datetime
from urllib.request import urlopen
from flask import jsonify, render_template
from app import app
from app.forms import forms

@app.route('/weather')

def hw01_localweather():
    return app.send_static_file('hw01_localweather.html')

@app.route("/api/weather")
def api_weather():
    response = requests.get("https://air-quality-api.open-meteo.com/v1/air-quality?latitude=18.8037949&longitude=98.9499454&hourly=pm10,pm2_5,us_aqi&current=us_aqi,pm10,pm2_5&timezone=Asia%2FBangkok")
    # return jsonify(data_json)
    data = response.json()
    current = data.get("current", {}).copy()
    current.pop("interval", None)

    next_hr = {}
    hourly = data.get   ("hourly", {})
    times = hourly.get("time", [])

    if times and current.get("time") in times:
        current_index = times.index(current["time"])
        current_ordered = {
            "AQI_US": hourly.get("us_aqi", [])[current_index],
            "PM10": hourly.get("pm10", [])[current_index],
            "PM2.5": hourly.get("pm2_5", [])[current_index],
            "Time": times[current_index]
}
        if current_index + 1 < len(times):
            next_hr["AQI_US"] = hourly.get("us_aqi", [])[current_index + 1]
            next_hr["Time"] = times[current_index + 1]
            next_hr["PM10"] = hourly.get("pm10", [])[current_index + 1]
            next_hr["PM2.5"] = hourly.get("pm2_5", [])[current_index + 1]

    return jsonify({
        "current": current_ordered,
        "next_hr": next_hr
    })
    
@app.route('/hw03/prcp')
def hw03_prcp():

    url = "https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=7.0084&longitude=100.4767&start_date=2025-11-01&end_date=2025-12-07&daily=precipitation_sum&hourly=temperature_2m&timezone=Asia%2FBangkok"
    response = urlopen(url)
    r = response.read()
    data_json = json.loads(r)

    prcpDATA = []
    dayInMonth = []
    prcpOnly = []
    prcpTuple = []
    dayInMonthShort = []
    
    for day, prcp in zip(data_json['daily']['time'], data_json['daily']['precipitation_sum']):
        #print(f"{day}: {prcp} mm")
        prcpDATA.append((day, prcp))
        prcpOnly.append(prcp)
        
    def calculateDayOfWeek(dateStr):
        dateObj = datetime.strptime(dateStr, "%Y-%m-%d")
        return dateObj.strftime("%A")
    
    for dateStr, _ in prcpDATA:
        dayOfWeek = calculateDayOfWeek(dateStr)
        dayInMonth.append(dayOfWeek) 
        
    for day in dayInMonth:
        dayInMonthShort.append(day[:2])
    
    for i in range(len(dayInMonth)):
        prcpTuple.append((dayInMonthShort[i], prcpOnly[i]))
        
    return render_template('lab03/hw03_prcp.html', data=prcpDATA, days=dayInMonthShort, tup=prcpTuple)

@app.route('/hw06/register', methods=('GET', 'POST'))
def hw06_register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        raw_json = read_file('data/users.json')
        users = json.loads(raw_json)
        users.append({'username': form.username.data,
                      'email': form.email.data,
                      'password': form.password.data,
                      })
        write_file('data/users.json',
                   json.dumps(users, indent=4))
        return redirect(url_for('hw06_users'))
    return render_template('lab06/hw06_register.html', form=form)

@app.route('/hw06/users', methods=('GET', 'POST'))
def hw06_users():
    raw_json = read_file('data/users.json')
    userList = json.loads(raw_json)
    return render_template('lab06/hw06_users.html', userList=userList)