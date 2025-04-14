# backend/process_level3.py
def process_level3(storm_data):
    points = []
    # Check if storm_data is from /stormcells (array of storm cells)
    if isinstance(storm_data, list):
        for storm in storm_data:
            ob = storm.get('ob', {})
            loc = storm.get('loc', {})
            points.append({
                'lat': loc.get('lat', 0),
                'lon': loc.get('long', 0),
                'shear': ob.get('mda', 0),  # Use MDA as shear proxy
                'type': 'TVS' if ob.get('tvs', 0) == 1 else ('MESO' if ob.get('mda', 0) > 0 else 'NONE'),
                'time': ob.get('dateTimeISO', 'Unknown')
            })
    # Handle NWS RIDGE GeoJSON format
    elif isinstance(storm_data, dict) and storm_data.get('type') == 'FeatureCollection':
        for feature in storm_data.get('features', []):
            coords = feature['geometry']['coordinates']
            properties = feature['properties']
            points.append({
                'lat': coords[1],
                'lon': coords[0],
                'shear': properties.get('shear', 0),
                'type': properties.get('type', 'TVS'),  # 'TVS' or 'MESO'
                'time': properties.get('timestamp', 'Unknown')
            })
    # Handle /observations format
    elif isinstance(storm_data, dict) and 'ob' in storm_data:
        ob = storm_data['ob']
        loc = storm_data['loc']
        wind_speed = ob.get('windSpeedMPH', 0)
        points.append({
            'lat': loc['lat'],
            'lon': loc['long'],
            'shear': wind_speed,
            'type': 'MESO' if wind_speed > 30 else 'NONE',
            'time': ob.get('timestamp', 'Unknown')
        })
    elif isinstance(storm_data, list):
        return points  # Return empty list if no data
    else:
        for tvs in storm_data.get('response', []):
            points.append({
                'lat': tvs['loc']['lat'],
                'lon': tvs['loc']['long'],
                'shear': tvs.get('shear', 0),
                'type': tvs['type'],  # 'TVS' or 'MESO'
                'time': tvs.get('timestamp', 'Unknown')
            })
    return points

if __name__ == '__main__':
    from fetch_level3 import fetch_level3_tvs
    tvs_result = fetch_level3_tvs()
    print(process_level3(tvs_result['data']))