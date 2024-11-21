from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
import os
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Look for .env file in the parent directory (root of project)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

@app.route('/api/nearby-attractions/<float:latitude>/<float:longitude>')
def get_nearby_attractions(latitude, longitude):
    if not GOOGLE_PLACES_API_KEY:
        return jsonify({"error": "Google Places API key not configured"}), 500
    radius = 5000
    place_type = 'tourist_attraction'
    
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'type': place_type,
        'key': GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'results' not in data:
            return jsonify([])
            
        attractions = [{
            'id': place['place_id'],
            'name': place['name'],
            'description': place.get('vicinity', ''),
            'rating': place.get('rating', 0),
            'photos': place.get('photos', []),
            'location': place['geometry']['location']
        } for place in data['results']]
        
        return jsonify(attractions)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify([])

@app.route('/')
def test():
    return jsonify({"message": "Server is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 