# backend/test_aerisweather.py
import requests

def test_aerisweather():
    try:
        api_key = '2qRfyRrVeDB22pw0Z2mCbAiJrHS0G0FLVi9wLR3Z'  # AerisWeather API secret
        client_id = 'HIXM4oS25l3yBhWDFrM4k'  # AerisWeather client ID
        # Test with a current observations endpoint for Seattle, WA
        url = f'https://api.aerisapi.com/observations/seattle,wa?client_id={client_id}&client_secret={api_key}'
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_aerisweather()