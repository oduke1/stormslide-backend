import logging
from logging.handlers import RotatingFileHandler
import sys
from flask import Flask, jsonify, send_from_directory, abort, render_template
from datetime import datetime, timedelta
import xarray as xr
import pytz
import json
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import s3fs

# Debug Logging for Python environment
logging.debug(f"Python executable: {sys.executable}")
logging.debug(f"sys.path: {sys.path}")
try:
    import matplotlib
    logging.debug(f"matplotlib version: {matplotlib.__version__}")
except ImportError as e:
    logging.error(f"Failed to import matplotlib: {str(e)}")
try:
    import cartopy
    logging.debug(f"cartopy version: {cartopy.__version__}")
except ImportError as e:
    logging.error(f"Failed to import cartopy: {str(e)}")
try:
    import numpy
    logging.debug(f"numpy version: {numpy.__version__}")
except ImportError as e:
    logging.error(f"Failed to import numpy: {str(e)}")

# Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File handler - log to /home/ubuntu/stormslide/flask_app.log
handler = RotatingFileHandler('/home/ubuntu/stormslide/flask_app.log', maxBytes=10000000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Add StreamHandler for debugging to stderr
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/radar')
def radar():
    logger.info("Test log: Entering /radar endpoint")
    handler.flush()
    try:
        # Define base time for the GFS data (use a historical date for availability)
        base_time = datetime(2025, 4, 1, 12, tzinfo=pytz.UTC)  # Changed to 2025-04-01
        gfs_date_str = base_time.strftime("%Y%m%d")

        # Ensure the static/radar directory exists
        radar_dir = '/home/ubuntu/stormslide/static/radar/'
        try:
            os.makedirs(radar_dir, exist_ok=True)
            logger.debug(f"Ensuring radar directory exists: {radar_dir}")
        except Exception as e:
            logger.error(f"Failed to create radar directory {radar_dir}: {str(e)}")
            return jsonify({'error': f"Failed to create radar directory: {str(e)}"}), 500

        # Use s3fs to access GFS files directly from S3
        try:
            fs = s3fs.S3FileSystem(anon=True)  # Anonymous access for public NOAA bucket
        except Exception as e:
            logger.error(f"Failed to initialize S3FileSystem: {str(e)}")
            return jsonify({'error': f"Failed to initialize S3 access: {str(e)}"}), 500

        bucket = 'noaa-gfs-bdp-pds'

        forecast = []
        for i in range(0, 361, 24):  # f000 to f360, every 24 hours
            logger.debug(f"Processing forecast hour f{i:03d}")
            forecast_time = base_time + timedelta(hours=i)
            s3_path = f"s3://{bucket}/gfs.{gfs_date_str}/12/atmos/gfs.t12z.pgrb2.0p25.f{i:03d}"
            output_file = os.path.join(radar_dir, f"gfs.t12z.pgrb2.0p25.f{i:03d}.png")
            logger.debug(f"Accessing GFS file from S3: {s3_path}")

            try:
                # Stream the GFS file from S3
                ds = xr.open_dataset(fs.open(s3_path), engine='cfgrib', backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface', 'stepType': 'instant'}})
                logger.debug(f"Loaded dataset for GFS f{i:03d}")
            except Exception as e:
                logger.error(f"Failed to load GFS file {s3_path}: {str(e)}")
                continue

            # Extract precipitation rate
            try:
                precip = ds['prate'].mean(dim=['latitude', 'longitude']).values
                logger.debug(f"Calculated mean precipitation: {precip}")
            except Exception as e:
                logger.error(f"Failed to calculate precipitation for {s3_path}: {str(e)}")
                continue

            # Generate PNG using matplotlib and cartopy
            logger.debug(f"Generating PNG: {output_file}")
            try:
                fig = plt.figure(figsize=(15, 10), dpi=80, facecolor='none', edgecolor='none')
                ax = plt.axes(projection=ccrs.PlateCarree(), facecolor='none')
                ax.set_extent([-125, -66, 23, 50], crs=ccrs.PlateCarree())
                ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)
                ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=0.5)
                ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=0.5)

                ax.set_facecolor('none')
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)

                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_xticklabels([])
                ax.set_yticklabels([])

                lats = ds['latitude'].values
                lons = ds['longitude'].values
                precip_data = ds['prate'].values * 3600
                levels = np.linspace(0, max(np.max(precip_data), 0.1), 20)
                cf = ax.contourf(lons, lats, precip_data, levels=levels, cmap='Blues', transform=ccrs.PlateCarree(), alpha=0.8, antialiased=True)

                plt.savefig(output_file, bbox_inches='tight', pad_inches=0.0, transparent=True)
                plt.close(fig)
                logger.debug(f"PNG generated: {output_file}")
            except Exception as e:
                logger.error(f"Failed to generate PNG {output_file}: {str(e)}")
                continue

            if not os.path.exists(output_file):
                logger.error(f"Failed to create PNG: {output_file}")
                continue

            try:
                os.chmod(output_file, 0o644)
                logger.debug(f"Set permissions for PNG: {output_file}")
            except Exception as e:
                logger.error(f"Failed to set permissions for PNG {output_file}: {str(e)}")
                continue

            forecast.append({
                'image': f"/radar/image/gfs.t12z.pgrb2.0p25.f{i:03d}.png",
                'precip': [float(precip), 0.0],
                'time': forecast_time.isoformat(),
                'timestamp': forecast_time.isoformat()
            })
            logger.info(f"Added forecast entry: timestamp={forecast_time.isoformat()}")
            handler.flush()

        if not forecast:
            logger.error("No forecast data generated")
            return jsonify({'error': 'No forecast data generated'}), 500

        logger.debug(f"Returning forecast with {len(forecast)} entries")
        return jsonify({'forecast': forecast, 'historical': []})
    except Exception as e:
        logger.error(f"Error in /radar: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/radar/image/<filename>')
def serve_radar_image(filename):
    radar_dir = '/home/ubuntu/stormslide/static/radar/'
    logger.debug(f"Serving radar image: {filename}")
    try:
        return send_from_directory(radar_dir, filename)
    except Exception as e:
        logger.error(f"Error serving radar image {filename}: {str(e)}")
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)