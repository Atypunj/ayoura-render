from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import swisseph as swe
import requests

app = Flask(__name__)
swe.set_ephe_path("./swisseph_data")

signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

planet_lords = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

def get_coordinates(place_name):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={place_name}"
    headers = {"User-Agent": "astro-api/1.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 and response.text.strip():
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print("Geocoding error:", e)
    return 0.0, 0.0

def calculate_astrology_details(dob, tob, place):
    birth_datetime = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    jd = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day,
                    birth_datetime.hour + birth_datetime.minute / 60)

    lat, lon = get_coordinates(place)
    houses, _ = swe.houses(jd, lat, lon)
    asc = houses[0]
    lagna_sign = int(asc / 30) + 1

    sun_long = swe.calc_ut(jd, swe.SUN)[0]
    moon_long = swe.calc_ut(jd, swe.MOON)[0]

    sun_sign = int(sun_long / 30) + 1
    moon_sign = int(moon_long / 30) + 1

    lagna = signs[lagna_sign - 1]
    rasi = signs[moon_sign - 1]
    sun = signs[sun_sign - 1]

    return {
        "lagna": lagna,
        "lagna_lord": planet_lords.get(lagna, "Unknown"),
        "rasi": rasi,
        "rasi_lord": planet_lords.get(rasi, "Unknown"),
        "indian_sun_sign": sun,
        "western_sun_sign": sun,
        "current_dasha": {"planet": "Mars", "start": "2020-04", "end": "2027-04"},
        "current_antardasha": {"planet": "Moon", "start": "2024-11", "end": "2025-09"},
        "weak_planet": "Saturn",
        "remedies": [
            "Chant Hanuman Chalisa on Saturdays",
            "Wear a blue sapphire after consulting an astrologer",
            "Offer oil to Shani temple on Saturdays"
        ]
    }

@app.route('/')
def form():
    return render_template_string("""
    <html>
    <head><title>Astrology API</title></head>
    <body style="font-family:Arial; padding:30px;">
        <h2>🧘 Enter Your Birth Details</h2>
        <form action="/astro-summary" method="get">
            <label>Date of Birth (YYYY-MM-DD):</label><br>
            <input name="dob" required><br><br>
            <label>Time of Birth (HH:MM 24hr):</label><br>
            <input name="tob" required><br><br>
            <label>Place of Birth:</label><br>
            <input name="place" required><br><br>
            <button type="submit">Get Astrology Summary</button>
        </form>
    </body>
    </html>
    """)

@app.route('/astro-summary', methods=['GET'])
def astro_summary():
    dob = request.args.get('dob')
    tob = request.args.get('tob')
    place = request.args.get('place')

    if not dob or not tob or not place:
        return jsonify({"error": "Missing required parameters: dob, tob, place"}), 400

    details = calculate_astrology_details(dob, tob, place)
    return jsonify(details)

if __name__ == '__main__':
    app.run(debug=True)
