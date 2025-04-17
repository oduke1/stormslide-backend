from flask import Flask, jsonify, Response
from fetch_level2 import fetch_latest_level2
from fetch_level3 import fetch_level3_tvs
from combine_data import combine_tornado_data
import requests
from flask_cors import CORS
import logging
from cachetools import TTLCache
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://stormslide.net"}})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for 10 minutes (600 seconds)
weather_cache = TTLCache(maxsize=1, ttl=600)
tornadoes_cache = TTLCache(maxsize=1, ttl=600)

def check_rate_limit(response):
    """Check Xweather rate-limit headers and delay if necessary."""
    remaining_minute = int(response.headers.get('X-RateLimit-Remaining-Minute', 999))
    remaining_period = int(response.headers.get('X-RateLimit-Remaining-Period', 999))
    reset_minute = response.headers.get('X-RateLimit-Reset-Minute', None)
    
    logger.info(f"Rate limits - Remaining Minute: {remaining_minute}, Remaining Period: {remaining_period}, Reset Minute: {reset_minute}")
    
    if remaining_minute <= 5:
        logger.warning("Nearing minutely rate limit, delaying request")
        time.sleep(5)

@app.route('/tornadoes')
def get_tornadoes():
    try:
        # Check if data is in cache
        if 'tornadoes' in tornadoes_cache:
            logger.info("Serving /tornadoes from cache")
            response_data = tornadoes_cache['tornadoes']
            flask_response = Response(response_data['content'], status=response_data['status'], mimetype='application/json')
            flask_response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
            return flask_response

        # Comment out simulated data
        # simulated_tornadoes = [
        #     {
        #         "latitude": 30.4383,
        #         "longitude": -84.2807,
        #         "source": "Level III",
        #         "type": "TVS",
        #         "shear": 70
        #     },
        #     {
        #         "latitude": 30.5,
        #         "longitude": -84.3,
        #         "source": "Level III",
        #         "type": "MESO",
        #         "shear": 50
        #     },
        #     {
        #         "latitude": 30.4,
        #         "longitude": -84.2,
        #         "source": "Level II",
        #         "shear": 60
        #     }
        # ]
        # response = jsonify(simulated_tornadoes)
        # response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        # tornadoes_cache['tornadoes'] = {'content': response.get_data(), 'status': 200}
        # return response

        l2_file = fetch_latest_level2()
        l3_data = fetch_level3_tvs()
        if not l2_file:
            logger.error("Failed to fetch Level II radar data")
            response = jsonify({'error': 'Failed to fetch Level II radar data'})
            response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
            tornadoes_cache['tornadoes'] = {'content': response.get_data(), 'status': 500}
            return response, 500

        # l3_data can be an empty list (valid response)
        tornadoes = combine_tornado_data(l2_file, l3_data if l3_data is not None else [])
        response = jsonify(tornadoes)
        response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        tornadoes_cache['tornadoes'] = {'content': response.get_data(), 'status': 200}
        return response
    except Exception as e:
        logger.error(f"Error in /tornadoes endpoint: {str(e)}", exc_info=True)
        response = jsonify({'error': f'Server error: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        tornadoes_cache['tornadoes'] = {'content': response.get_data(), 'status': 500}
        return response, 500

@app.route('/proxy-weather')
def proxy_weather():
    try:
        # Check if data is in cache
        if 'weather' in weather_cache:
            logger.info("Serving /proxy-weather from cache")
            response_data = weather_cache['weather']
            flask_response = Response(response_data['content'], status=response_data['status'], mimetype='application/json')
            flask_response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
            return flask_response

        client_id = 'HIXM4oS25l3yBhWDFrM4k'
        client_secret = '2qRfyRrVeDB22pw0Z2mCbAiJrHS0G0FLVi9wLR3Z'
        url = f'https://api.aerisapi.com/conditions/tallahassee,fl?limit=1&client_id={client_id}&client_secret={client_secret}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        check_rate_limit(response)
        flask_response = Response(response.content, status=response.status_code, mimetype='application/json')
        flask_response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        weather_cache['weather'] = {'content': response.content, 'status': response.status_code}
        return flask_response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Xweather data: {str(e)}", exc_info=True)
        response = jsonify({"error": f"Failed to fetch weather data: {str(e)}"})
        response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        weather_cache['weather'] = {'content': response.get_data(), 'status': 502}
        return response, 502
    except Exception as e:
        logger.error(f"Error in /proxy-weather endpoint: {str(e)}", exc_info=True)
        response = jsonify({"error": f"Server error: {str(e)}"})
        response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        weather_cache['weather'] = {'content': response.get_data(), 'status': 500}
        return response, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)