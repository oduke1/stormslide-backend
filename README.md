# StormSlide

A tornado mapping app that uses NEXRAD Level II and Level III radar data to detect and visualize tornadoes on a map.

## Structure

- `backend/`: Python scripts for processing radar data and serving the API.
- `frontend/`: JavaScript and HTML for the MapLibre-based UI.
- `scripts/`: Utility scripts (e.g., deployment automation).
- `data/`: Cached radar data (ignored by Git).

## Setup

1. Clone the repository: `git clone https://github.com/oduke1/stormslide-backend.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the Flask API: `cd backend && python api.py`
