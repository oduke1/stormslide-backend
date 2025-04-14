# backend/fetch_level3.py
import requests

def fetch_level3_tvs(radar_site='KTLH'):
    try:
        api_key = '2qRfyRrVeDB22pw0Z2mCbAiJrHS0G0FLVi9wLR3Z'  # AerisWeather API secret
        client_id = 'HIXM4oS25l3yBhWDFrM4k'  # AerisWeather client ID
        url = f'https://api.aerisapi.com/radar/tvs/{radar_site}?client_id={client_id}&client_secret={api_key}'
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            data = response.json()
            return {
                'success': data.get('success', False),
                'status_code': response.status_code,
                'data': data.get('response', []),
                'error': data.get('error', None)
            }
        return {
            'success': False,
            'status_code': response.status_code,
            'data': [],
            'error': f"HTTP {response.status_code}: {response.reason}"
        }
    except Exception as e:
        print(f"Error fetching Level III data: {e}")
        return {
            'success': False,
            'status_code': None,
            'data': [],
            'error': str(e)
        }

# Fallback: NWS RIDGE (uncomment to use if AerisWeather key fails)
# def fetch_level3_ridge(radar_site='KTLH'):
#     try:
#         url = f'https://radar.weather.gov/ridge/standard/{radar_site}_TVS.geojson'
#         response = requests.get(url, timeout=10)
#         if response.status_code == 200:
#             return response.json()
#         return []
#     except Exception as e:
#         print(f"Error fetching RIDGE data: {e}")
#         return []

if __name__ == '__main__':
    result = fetch_level3_tvs()
    print(result)