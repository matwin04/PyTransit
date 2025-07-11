from flask import Flask, render_template, jsonify
import gtfs_kit as gk

import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Load GTFS feed
FEED_PATH = "data/OC.zip"
feed = gk.read_feed(FEED_PATH, dist_units="km")

# TIME CONVERSION
def timestring_to_seconds(timestr):
    h, m, s = map(int, timestr.split(":"))
    return h * 3600 + m * 60 + s
def format_am_pm(sec):
    hour = (sec // 3600) % 24
    minute = (sec % 3600) // 60
    return datetime(2000, 1, 1, hour, minute).strftime("%I:%M %p")

#SERVER
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/stations")
def stations():
    stations = feed.stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]]
    stations = stations.sort_values("stop_name")
    return render_template("stations.html", stations=stations)
@app.route("/routes")
def routes():
    routes = feed.routes[["route_id","agency_id","route_short_name","route_long_name","route_type","route_url","route_color","route_text_color"]]
    return render_template("routes.html",routes=routes)

@app.route("/departures/<stop_id>")
def departures(stop_id):
    now = datetime.now()
    now_seconds = now.hour * 3600 + now.minute * 60 + now.second

    stop_times = feed.stop_times[feed.stop_times["stop_id"] == stop_id]
    stop_times = stop_times.merge(feed.trips, on="trip_id")
    stop_times = stop_times.merge(feed.routes, on="route_id", how="left")

    stop_times["seconds"] = stop_times["departure_time"].apply(timestring_to_seconds)
    upcoming = stop_times[stop_times["seconds"] >= now_seconds].copy()
    upcoming = upcoming.sort_values("seconds")

    upcoming["formatted_time"] = upcoming["seconds"].apply(format_am_pm)

    departures = upcoming[["trip_id", "formatted_time", "trip_headsign", "route_short_name", "route_color", "route_text_color"]].to_dict(orient="records")

    # 🔍 Lookup stop name from stops.txt
    stop_row = feed.stops[feed.stops["stop_id"] == stop_id]
    stop_name = stop_row["stop_name"].values[0] if not stop_row.empty else stop_id

    return render_template("departures.html", departures=departures, stop_id=stop_id, stop_name=stop_name)
if __name__ == "__main__":
    app.run(debug=True)