import logging
from logging.handlers import RotatingFileHandler
import sys
from flask import Flask, jsonify, send_from_directory, abort, render_template, request, redirect
from datetime import datetime, timedelta
import xarray as xr
from pytz import UTC
import json
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File handler for /var/log/flask_app.log
handler = RotatingFileHandler('/var/log/flask_app.log', maxBytes=10000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
handler.flush = lambda: handler.stream.flush()

# Add StreamHandler for debugging to stderr
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Log startup
logging.debug("Starting Flask app...")

app = Flask(__name__)
app.config['SERVER_NAME'] = 'stormslide.net'
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Middleware to enforce HTTPS with Cloudflare proxy
@app.before_request
def enforce_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

logging.debug("Flask app initialized.")

# Log before defining routes
logging.debug("About to define routes...")

# Define the homepage route
logging.debug("Defining homepage route...")
@app.route("/")
def home():
    logging.debug("Accessing homepage.")
    return render_template("index.html")
logging.debug("Homepage route defined.")

# Define the radar route
logging.debug("Defining radar route...")
@app.route('/radar')
def radar():
    try:
        logging.debug("Accessing /radar endpoint.")
        # Skip NEXRAD data fetching for now
        historical = []
        logging.debug("Skipping NEXRAD data fetching due to unavailable recent data in S3 bucket")

        # Fetch GFS data from local files
        forecast = []
        for i in range(0, 16 * 24, 24):  # Full range: f000 to f360
            try:
                local_file = f"/home/ubuntu/data/gfs/20250407/gfs.t12z.pgrb2.0p25.f{i:03d}"
                logging.debug(f"Reading GFS f{i:03d} from {local_file}")
                with open(local_file, 'rb') as f:
                    logging.debug(f"Successfully opened file {local_file}")
                data = xr.open_dataset(local_file, engine="cfgrib", backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface", "stepType": "instant"}})
                logging.debug(f"Loaded dataset for GFS f{i:03d}")
                precip = float(data["prate"].mean().values)
                logging.debug(f"GFS f{i:03d} precip: {precip}")
                # For now, use a placeholder image name (we'll generate real images in the next step)
                image_name = f"gfs.t12z.pgrb2.0p25.f{i:03d}.png"
                forecast.append({
                    "precip": [precip, 0.0],
                    "time": (datetime.now(UTC) + timedelta(hours=i)).isoformat(),
                    "timestamp": (datetime.now(UTC) + timedelta(hours=i)).isoformat(),
                    "image": image_name
                })
            except Exception as e:
                logging.error(f"Error processing GFS file f{i:03d}: {str(e)}")
                continue

        logging.debug("Returning radar data")
        return jsonify({"forecast": forecast, "historical": historical})
    except Exception as e:
        logging.error(f"Unexpected error in /radar endpoint: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
logging.debug("Radar route defined.")

# Define the radar image route
logging.debug("Defining radar image route...")
@app.route('/radar/image/<filename>')
def serve_radar_image(filename):
    radar_dir = os.path.join(app.root_path, 'static', 'radar')
    try:
        return send_from_directory(radar_dir, filename)
    except FileNotFoundError:
        abort(404, description=f"Radar image {filename} not found")
logging.debug("Radar image route defined.")

# Log after defining all routes
logging.debug("All routes defined.")

if __name__ == "__main__":
    logging.debug("Running Flask app on port 5000...")
    app.run(host="0.0.0.0", port=5000, threaded=True)