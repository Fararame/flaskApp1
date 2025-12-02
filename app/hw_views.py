# Maythanan Ladee (Frame)
# 670510722
# sec001

import requests
import json
from datetime import datetime
from urllib.request import urlopen
from flask import jsonify
from app import app

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