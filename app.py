from flask import Flask, render_template, request
import swisseph as swe
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form["name"]
        gender = request.form["gender"]
        date_str = request.form["dob"]
        time_str = request.form["tob"]
        place = request.form["pob"]

        # Convert to datetime
        dt = datetime.datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %I:%M %p")
        jd_ut = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

        moon_long = swe.calc_ut(jd_ut, swe.MOON)[0]
        result = {
            "name": name,
            "gender": gender,
            "moon_longitude": moon_long,
            "place": place
        }
    return render_template("blessings.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)