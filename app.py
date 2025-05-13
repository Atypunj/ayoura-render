from flask import Flask, render_template, request
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import datetime
import traceback

app = Flask(__name__)

nakshatras = [
    ("Ashwini", "Ketu", 0.0, 13.3333), ("Bharani", "Venus", 13.3333, 26.6666),
    ("Krittika", "Sun", 26.6666, 40.0), ("Rohini", "Moon", 40.0, 53.3333),
    ("Mrigashira", "Mars", 53.3333, 66.6666), ("Ardra", "Rahu", 66.6666, 80.0),
    ("Punarvasu", "Jupiter", 80.0, 93.3333), ("Pushya", "Saturn", 93.3333, 106.6666),
    ("Ashlesha", "Mercury", 106.6666, 120.0), ("Magha", "Ketu", 120.0, 133.3333),
    ("Purva Phalguni", "Venus", 133.3333, 146.6666), ("Uttara Phalguni", "Sun", 146.6666, 160.0),
    ("Hasta", "Moon", 160.0, 173.3333), ("Chitra", "Mars", 173.3333, 186.6666),
    ("Swati", "Rahu", 186.6666, 200.0), ("Vishakha", "Jupiter", 200.0, 213.3333),
    ("Anuradha", "Saturn", 213.3333, 226.6666), ("Jyeshtha", "Mercury", 226.6666, 240.0),
    ("Mula", "Ketu", 240.0, 253.3333), ("Purva Ashadha", "Venus", 253.3333, 266.6666),
    ("Uttara Ashadha", "Sun", 266.6666, 280.0), ("Shravana", "Moon", 280.0, 293.3333),
    ("Dhanishta", "Mars", 293.3333, 306.6666), ("Shatabhisha", "Rahu", 306.6666, 320.0),
    ("Purva Bhadrapada", "Jupiter", 320.0, 333.3333), ("Uttara Bhadrapada", "Saturn", 333.3333, 346.6666),
    ("Revati", "Mercury", 346.6666, 360.0)
]

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    try:
        if request.method == "POST":
            name = request.form.get("name")
            gender = request.form.get("gender")
            date_str = request.form.get("dob")
            time_str = request.form.get("tob")
            place = request.form.get("pob")
            lat_str = request.form.get("lat", "28.4089")
            lon_str = request.form.get("lon", "77.3178")

            # Convert to float to avoid invalid int() errors
            lat = float(lat_str)
            lon = float(lon_str)

            dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %I:%M %p")
            dob = Datetime(dt.strftime("%Y/%m/%d"), dt.strftime("%H:%M"), '+05:30')  # IST

            print(f"Using coordinates: {lat}, {lon}")
            pos = GeoPos(str(lat), str(lon))
            chart = Chart(dob, pos)

            moon = chart.get('MOON')
            asc = chart.get('ASC')
            moon_lon = float(moon.lon)
            nakshatra_name = None
            for nak in nakshatras:
                if nak[2] <= moon_lon < nak[3]:
                    nakshatra_name = nak[0]
                    break

            result = {
                "name": name,
                "gender": gender,
                "dob": date_str,
                "tob": time_str,
                "pob": place,
                "rashi": moon.sign,
                "nakshatra": nakshatra_name,
                "ascendant": asc.sign
            }

    except Exception as e:
        error = traceback.format_exc()
        print("Error:", error)

    return render_template("blessings.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
