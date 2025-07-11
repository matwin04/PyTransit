from flask import Flask, render_template, jsonify
import gtfs_kit as gk
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Load GTFS feed
FEED_PATH = "data/OC.zip"
feed = gk.read_feed(FEED_PATH, dist_units="km")

@app.route("/")
def home():
    return "<h2>Welcome to the OC GTFS Viewer</h2><p>Go to /stations or /departures/&lt;stop_id&gt;</p>"

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
    now = datetime.now().time()

    stop_times = feed.stop_times[feed.stop_times["stop_id"] == stop_id]
    stop_times = stop_times.merge(feed.trips, on="trip_id")
    stop_times = stop_times.merge(feed.routes, on="route_id", how="left")

    # Filter out past times
    stop_times["parsed_time"] = stop_times["departure_time"].apply(lambda t: datetime.strptime(t, "%H:%M:%S").time())
    upcoming = stop_times[stop_times["parsed_time"] >= now]

    # Sort by time
    upcoming = upcoming.sort_values("parsed_time")

    # Format time to 12-hour format
    upcoming["formatted_time"] = upcoming["parsed_time"].apply(lambda t: t.strftime("%I:%M %p"))

    departures = upcoming[["trip_id", "formatted_time", "trip_headsign", "route_short_name", "route_color", "route_text_color"]].to_dict(orient="records")

    return render_template("departures.html", departures=departures, stop_id=stop_id)
if __name__ == "__main__":
    app.run(debug=True)