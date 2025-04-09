import logging
from logging.handlers import RotatingFileHandler
import sys
from flask import Flask, jsonify
from datetime import datetime, timedelta
import xarray as xr
from pytz import UTC
import json

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
app.config['SERVER_NAME'] = None
app.config['PREFERRED_URL_SCHEME'] = 'https'

logging.debug("Flask app initialized.")

# Log before defining routes
logging.debug("About to define routes...")

# Define the homepage route
logging.debug("Defining homepage route...")
@app.route("/")
def home():
    logging.debug("Accessing homepage.")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>StormSlide Radar App</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background: #f0f0f0; }
            h1 { color: #1a73e8; }
            p { font-size: 1.2em; }
            a { color: #1a73e8; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>StormSlide Radar App</h1>
        <p>Live radar + 16-day forecasts, powered by AI.</p>
        <p>Android app coming soon to Google Play!</p>
        <p><a href="/radar">View Raw Radar Data (JSON)</a></p>
    </body>
    </html>
    """
logging.debug("Homepage route defined.")

# Define the radar route
logging.debug("Defining radar route...")
@app.route('/radar')
def radar():
    try:
        logging.debug("Accessing /radar endpoint.")
        # Skip NEXRAD data fetching for now due to lack of recent data in S3 bucket
        historical = []
        logging.debug("Skipping NEXRAD data fetching due to unavailable recent data in S3 bucket")

        # Fetch GFS data (pre-fetched) from local files
        forecast = []
        for i in range(0, 16 * 24, 24):  # Full range: f000 to f360
            try:
                local_file = f"/home/ubuntu/data/gfs/20250407/gfs.t12z.pgrb2.0p25.f{i:03d}"
                logging.debug(f"Reading GFS f{i:03d} from {local_file}")
                # Test file access before loading
                with open(local_file, 'rb') as f:
                    logging.debug(f"Successfully opened file {local_file}")
                data = xr.open_dataset(local_file, engine="cfgrib", backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface", "stepType": "instant"}})
                logging.debug(f"Loaded dataset for GFS f{i:03d}")
                precip = float(data["prate"].mean().values)
                logging.debug(f"GFS f{i:03d} precip: {precip}")
                forecast.append({"precip": [precip, 0.0], "time": (datetime.now(UTC) + timedelta(hours=i)).isoformat()})
            except Exception as e:
                logging.error(f"Error processing GFS file f{i:03d}: {str(e)}")
                continue  # Skip this file and continue with the next one

        logging.debug("Returning radar data")
        return jsonify({"forecast": forecast, "historical": historical})
    except Exception as e:
        logging.error(f"Unexpected error in /radar endpoint: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
logging.debug("Radar route defined.")

# Log after defining all routes
logging.debug("All routes defined.")

if __name__ == "__main__":
    logging.debug("Running Flask app on port 5000...")
    app.run(host="0.0.0.0", port=5000, threaded=True)
