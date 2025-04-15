from flask import Flask, jsonify, Response
from fetch_level2 import fetch_latest_level2
from fetch_level3 import fetch_level3_tvs
from combine_data import combine_tornado_data
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://stormslide.net"}})

@app.route('/tornadoes')
def get_tornadoes():
    l2_file = fetch_latest_level2()
    l3_data = fetch_level3_tvs()
    if not l2_file:  # Only fail if Level II data fetch fails
        response = jsonify({'error': 'Failed to fetch Level II radar data'})
        response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        return response, 500
    # l3_data can be an empty list (valid response)
    tornadoes = combine_tornado_data(l2_file, l3_data if l3_data is not None else [])
    response = jsonify(tornadoes)
    response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
    return response

@app.route('/proxy-weather')
def proxy_weather():
    client_id = 'HIXM4oS25l3yBhWDFrM4k'
    client_secret = '2qRfyRrVeDB22pw0Z2mCbAiJrHS0G0FLVi9wLR3Z'
    url = f'https://api.aerisapi.com/conditions/tallahassee,fl?limit=1&client_id={client_id}&client_secret={client_secret}'
    try:
        response = requests.get(url)
        flask_response = Response(response.content, status=response.status_code, mimetype='application/json')
        flask_response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        return flask_response
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'https://stormslide.net')
        return response, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)