from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
import os
from pathlib import Path
from flask_cors import CORS
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app)

# Look for .env file in the parent directory (root of project)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

@app.route('/api/nearby-attractions/<float:latitude>/<float:longitude>/<int:radius>')
def get_nearby_attractions(latitude, longitude, radius):
    if not GOOGLE_PLACES_API_KEY:
        return jsonify({"error": "Google Places API key not configured"}), 500
    
    # Default radius if not specified or invalid
    if radius <= 0:
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

@app.route('/api/place-details/<place_id>')
def get_place_details(place_id):
    if not GOOGLE_PLACES_API_KEY:
        return jsonify({"error": "Google Places API key not configured"}), 500
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'photos,reviews',
        'key': GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'result' not in data:
            return jsonify({})
        
        result = data['result']
        photos = []
        
        if 'photos' in result:
            for photo in result['photos'][:5]:  # Limit to 5 photos
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo"
                photo_params = {
                    'maxwidth': 800,
                    'photo_reference': photo['photo_reference'],
                    'key': GOOGLE_PLACES_API_KEY
                }
                photos.append(f"{photo_url}?{urlencode(photo_params)}")
        
        return jsonify({
            'photos': photos,
            'reviews': result.get('reviews', [])
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({})

@app.route('/')
def test():
    return jsonify({"message": "Server is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 