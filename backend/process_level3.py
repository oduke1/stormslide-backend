# backend/process_level3.py
def process_level3(tvs_data):
    points = []
    for tvs in tvs_data.get('response', []):
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
    tvs_data = fetch_level3_tvs()
    print(process_level3(tvs_data))