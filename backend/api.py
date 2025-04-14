# backend/api.py
from flask import Flask, jsonify
from fetch_level2 import fetch_latest_level2
from fetch_level3 import fetch_level3_tvs
from combine_data import combine_tornado_data

app = Flask(__name__)

@app.route('/tornadoes')
def get_tornadoes():
    l2_file = fetch_latest_level2()
    l3_data = fetch_level3_tvs()
    if not l2_file:  # Only fail if Level II data fetch fails
        return jsonify({'error': 'Failed to fetch Level II radar data'}), 500
    # l3_data can be an empty list (valid response)
    tornadoes = combine_tornado_data(l2_file, l3_data if l3_data is not None else [])
    return jsonify(tornadoes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)