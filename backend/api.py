from flask import Flask, jsonify, Response
from fetch_level2 import fetch_latest_level2
from fetch_level3 import fetch_level3_tvs
from combine_data import combine_tornado_data
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://stormslide.net"}})  # Allow requests from stormslide.net

@app.route('/tornadoes')
def get_tornadoes():
    l2_file = fetch_latest_level2()
    l3_data = fetch_level3_tvs()
    if not l2_file:  # Only fail if Level II data fetch fails
        return jsonify({'error': 'Failed to fetch Level II radar data'}), 500
    # l3_data can be an empty list (valid response)
    tornadoes = combine_tornado_data(l2_file, l3_data if l3_data is not None else [])
    return jsonify(tornadoes)

@app.route('/proxy-weather')
def proxy_weather():
    url = 'https://weather.googleapis.com/v1/currentConditions?lat=30.4383&lng=-84.2807&key=AIzaSyCF9AtJmtOqIVDDciiETJFhP06trEtbxjA'
    try:
        response = requests.get(url)
        return Response(response.content, status=response.status_code, mimetype='application/json')
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)