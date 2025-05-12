
from flask import Flask, render_template, request
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import datetime
import requests

app = Flask(__name__)

def get_coordinates(place):
    try:
        response = requests.get("https://nominatim.openstreetmap.org/search", params={
            "q": place,
            "format": "json",
            "limit": 1,
            "countrycodes": "in"
        }, headers={"User-Agent": "AyouraSkyApp"})
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
    except Exception as e:
        print("Error fetching coordinates:", e)
    return None, None

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

            lat, lon = get_coordinates(place)
            print("LatLon debug:", lat, lon)

            if not lat or not lon:
                result = {"error": "Could not retrieve coordinates for the selected place."}
                return render_template("blessings.html", result=result)

            pos = GeoPos(float(lat), float(lon))

            try:
                chart = Chart(dob, pos)
            except IndexError:
                result = {"error": "Astrological data could not be computed. Please try a nearby known place."}
                return render_template("blessings.html", result=result)

            moon = chart.get(const.MOON)
            asc = chart.get(const.ASC)
            nakshatra = moon.nakshatra
            mahadasha = moon.sign  # Simplified example for Mahadasha placeholder

            result = {
                "name": name,
                "gender": gender,
                "place": place,
                "moon_sign": moon.sign,
                "ascendant": asc.sign,
                "nakshatra": nakshatra,
                "mahadasha": mahadasha
            }
        except Exception as e:
            print("ERROR OCCURRED:", str(e))
            result = {"error": "There was a problem processing your input."}

    return render_template("blessings.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
