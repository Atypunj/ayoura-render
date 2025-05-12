from flask import Flask, render_template, request
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        date_str = request.form.get("dob")
        time_str = request.form.get("tob")
        place = request.form.get("pob")  # make sure your form uses name="pob"

        try:
            dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
            dob = Datetime(dt.strftime("%Y/%m/%d"), dt.strftime("%H:%M"), '+05:30')  # IST
            pos = GeoPos("28.4089", "77.3178")  # Faridabad fallback

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
            result = {"error": "Something went wrong. Please check input format."}

    return render_template("blessings.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
