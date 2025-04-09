import logging
import xarray as xr

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    logging.debug("Reading GFS f360 file...")
    local_file = "/home/ubuntu/data/gfs/20250407/gfs.t12z.pgrb2.0p25.f360"
    data = xr.open_dataset(local_file, engine="cfgrib", backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface", "stepType": "instant"}})
    logging.debug("Loaded dataset successfully.")
    precip = float(data["prate"].mean().values)
    logging.debug(f"GFS f360 precip: {precip}")
except Exception as e:
    logging.error(f"Error processing GFS f360 file: {str(e)}")
