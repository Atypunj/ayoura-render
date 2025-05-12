from flask import Flask, render_template, request
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import datetime
import requests

app = Flask(__name__)

def get_lat_lon(place):
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=in&q={place}"
        response = requests.get(url, headers={"User-Agent": "AyouraApp"})
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print("Geo lookup failed:", e)
    return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        date_str = request.form.get("dob")
        time_str = request.form.get("tob")
        place = request.form.get("pob")

        try:
            lat, lon = get_lat_lon(place)
            if lat is None or lon is None:
                raise ValueError("Astrological data could not be computed. Please try a nearby known place.")

            dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
            dob = Datetime(dt.strftime("%Y/%m/%d"), dt.strftime("%H:%M"), '+05:30')
            pos = GeoPos(str(lat), str(lon))
            chart = Chart(dob, pos)

            moon = chart.get(const.MOON)
            asc = chart.get(const.ASC)

            result = {
                "name": name,
                "gender": gender,
                "place": place,
                "moon_sign": moon.sign,
                "ascendant": asc.sign,
                "nakshatra": moon.nakshatra,
                "mahadasha": "To be calculated"
            }
        except Exception as e:
            result = {"error": str(e)}

    return render_template("blessings.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
