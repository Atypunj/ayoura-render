from flask import Flask, render_template, request
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import datetime
import requests

app = Flask(__name__)

# Function to convert float to D:M:S format for flatlib
def float_to_dms(value):
    degrees = int(value)
    minutes = int((abs(value) - abs(degrees)) * 60)
    seconds = int((((abs(value) - abs(degrees)) * 60) - minutes) * 60)
    return f"{degrees}:{minutes}:{seconds}"

# Geocoding function
def geocode_place(place):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place, "format": "json", "limit": 1}
        headers = {"User-Agent": "AyouraAstroApp"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        if data:
            lat = float_to_dms(float(data[0]["lat"]))
            lon = float_to_dms(float(data[0]["lon"]))
            return lat, lon
    except Exception as e:
        print("Geocoding error:", e)
    return float_to_dms(28.4089), float_to_dms(77.3178)  # Default: Faridabad

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            name = request.form.get("name")
            gender = request.form.get("gender")
            date_str = request.form.get("dob")
            time_str = request.form.get("tob")
            place = request.form.get("pob")

            dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
            dob = Datetime(dt.strftime("%Y/%m/%d"), dt.strftime("%H:%M"), '+05:30')
            lat, lon = geocode_place(place)
            pos = GeoPos(lat, lon)

            chart = Chart(dob, pos)
            moon = chart.get('MOON')
            asc = chart.get('ASC')

            result = {
                "name": name,
                "gender": gender,
                "moon_sign": moon.sign,
                "ascendant": asc.sign,
                "place": place
            }

        except Exception as e:
            print("Error:", e)
            result = {"error": "There was a problem processing your input. Try a nearby city or simpler place name."}

    return render_template("blessings.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
