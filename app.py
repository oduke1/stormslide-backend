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

# File handler - log to /var/log/flask_app.log
handler = RotatingFileHandler('/var/log/flask_app.log', maxBytes=10000000, backupCount=1)
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
    logger.debug("Received request for /radar")
    try:
        # Define base time for the GFS data
        base_time = datetime(2025, 4, 7, 12, tzinfo=pytz.UTC)
        gfs_dir = '/home/ubuntu/data/gfs/20250407/'
        logger.debug(f"Looking for GFS data in: {gfs_dir}")

        # Check if the GFS directory exists
        if not os.path.exists(gfs_dir):
            logger.error(f"GFS directory not found: {gfs_dir}")
            return jsonify({'error': 'GFS data directory not found'}), 500

        # Ensure the static/radar directory exists
        radar_dir = '/home/ubuntu/stormslide/static/radar/'
        try:
            os.makedirs(radar_dir, exist_ok=True)
            logger.debug(f"Ensuring radar directory exists: {radar_dir}")
        except Exception as e:
            logger.error(f"Failed to create radar directory {radar_dir}: {str(e)}")
            return jsonify({'error': f"Failed to create radar directory: {str(e)}"}), 500

        forecast = []
        for i in range(0, 361, 24):  # f000 to f360, every 24 hours
            logger.debug(f"Processing forecast hour f{i:03d}")
            forecast_time = base_time + timedelta(hours=i)
            file_path = os.path.join(gfs_dir, f"gfs.t12z.pgrb2.0p25.f{i:03d}")
            
            # Check if the GFS file exists
            if not os.path.exists(file_path):
                logger.error(f"GFS file not found: {file_path}")
                continue

            # Load the GFS data
            logger.debug(f"Loading GFS file: {file_path}")
            try:
                ds = xr.open_dataset(file_path, engine='cfgrib', backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface'}})
            except Exception as e:
                logger.error(f"Failed to load GFS file {file_path}: {str(e)}")
                continue
            
            # Extract precipitation rate
            try:
                precip = ds['prate'].mean(dim=['latitude', 'longitude']).values
                logger.debug(f"Calculated mean precipitation: {precip}")
            except Exception as e:
                logger.error(f"Failed to calculate precipitation for {file_path}: {str(e)}")
                continue

            # Generate PNG using matplotlib and cartopy
            output_file = os.path.join(radar_dir, f"gfs.t12z.pgrb2.0p25.f{i:03d}.png")
            logger.debug(f"Generating PNG: {output_file}")

            try:
                # Create a plot with fully transparent background
                fig = plt.figure(figsize=(12, 8), dpi=100, facecolor='none', edgecolor='none')
                ax = plt.axes(projection=ccrs.PlateCarree(), facecolor='none')
                ax.set_extent([-125, -66, 25, 50], crs=ccrs.PlateCarree())  # Continental US
                ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)
                ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=0.5)
                ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=0.5)

                # Ensure axes background is transparent
                ax.set_facecolor('none')
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)

                # Plot precipitation (convert prate to mm/h)
                lats = ds['latitude'].values
                lons = ds['longitude'].values
                precip_data = ds['prate'].values * 3600  # Convert kg/m^2/s to mm/h
                levels = np.linspace(0, max(np.max(precip_data), 0.1), 20)  # Avoid zero max
                cf = ax.contourf(lons, lats, precip_data, levels=levels, cmap='Blues', transform=ccrs.PlateCarree(), alpha=0.8)

                # Add title (compact, at the top)
                plt.title(f"GFS Forecast: {forecast_time.strftime('%Y-%m-%d %H:%M UTC')}", fontsize=10, pad=5)

                # Save with tight layout and transparent background
                plt.savefig(output_file, bbox_inches='tight', pad_inches=0.05, transparent=True)
                plt.close(fig)
                logger.debug(f"PNG generated: {output_file}")
            except Exception as e:
                logger.error(f"Failed to generate PNG {output_file}: {str(e)}")
                continue

            # Ensure the file was created
            if not os.path.exists(output_file):
                logger.error(f"Failed to create PNG: {output_file}")
                continue

            # Ensure file permissions
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