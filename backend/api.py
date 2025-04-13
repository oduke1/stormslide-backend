# backend/api.py (refactored)
from flask import Flask, jsonify
from fetch_level2 import fetch_latest_level2
from fetch_level3 import fetch_level3_tvs
from combine_data import combine_tornado_data

app = Flask(__name__)

@app.route('/tornadoes')
def get_tornadoes():
    l2_file = fetch_latest_level2()
    l3_data = fetch_level3_tvs()
    if not l2_file or not l3_data:
        return jsonify({'error': 'Failed to fetch radar data'}), 500
    tornadoes = combine_tornado_data(l2_file, l3_data)
    return jsonify(tornadoes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)