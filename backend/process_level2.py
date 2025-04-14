# backend/process_level2.py
import pyart
import numpy as np

def process_level2(file_path, max_sweeps=5):  # Limit number of sweeps for testing
    try:
        radar = pyart.io.read_nexrad_archive(file_path)
        velocity = radar.fields['velocity']['data']  # Super-res velocity (m/s)
        reflectivity = radar.fields['reflectivity']['data']  # dBZ
        lats = radar.gate_latitude['data']
        lons = radar.gate_longitude['data']

        # Simplified storm motion (replace with NWS estimate or Bunkers method)
        storm_motion = 10  # m/s
        sr_velocity = velocity - storm_motion

        # Detect velocity couplets (limit to max_sweeps)
        couplets = []
        num_sweeps = min(sr_velocity.shape[0], max_sweeps)
        for i in range(num_sweeps):
            for j in range(sr_velocity.shape[1] - 1):
                shear = abs(sr_velocity[i, j] - sr_velocity[i, j + 1])
                # Ensure reflectivity[i, j] is a numeric value
                try:
                    refl_value = float(reflectivity[i, j]) if not isinstance(reflectivity[i, j], np.ma.MaskedConstant) else -999
                except (TypeError, AttributeError):
                    refl_value = -999  # Default to invalid value if data is corrupt
                if shear > 40 and refl_value > 50:  # TVS + debris threshold
                    couplets.append({
                        'lat': float(lats[i, j]),
                        'lon': float(lons[i, j]),
                        'shear': float(shear),
                        'type': 'TVS' if shear > 60 else 'MESO'
                    })
        return couplets
    except Exception as e:
        print(f"Error processing Level II data: {e}")
        return []

if __name__ == '__main__':
    from fetch_level2 import fetch_latest_level2
    file = fetch_latest_level2()
    if file:
        print(process_level2(file))
    else:
        print("Failed to fetch Level II file.")