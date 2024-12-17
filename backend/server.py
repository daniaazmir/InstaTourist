from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os
from pathlib import Path
from flask_cors import CORS
from urllib.parse import urlencode
from itinerary_generator import generate_itinerary
from datetime import datetime
import openai

app = Flask(__name__)
CORS(app)

# Look for .env file in the parent directory (root of project)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Add this near the top of your file, after setting the API keys
if not GOOGLE_PLACES_API_KEY or not openai.api_key:
    print("Warning: Missing API keys!")
    print("GOOGLE_PLACES_API_KEY:", "Present" if GOOGLE_PLACES_API_KEY else "Missing")
    print("OPENAI_API_KEY:", "Present" if openai.api_key else "Missing")

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

@app.route('/api/generate-itinerary', methods=['POST'])
def generate_itinerary():
    if not openai.api_key:
        return jsonify({"error": "OpenAI API key not configured"}), 500

    data = request.json
    attractions = data.get('attractions', [])
    preferences = data.get('preferences', {})
    
    if not attractions:
        return jsonify({"error": "No attractions provided"}), 400

    # Create a more detailed prompt for better results
    attractions_text = "\n".join([
        f"{i+1}. {a['name']} - {a['description']} (Rating: {a['rating']}★)"
        for i, a in enumerate(attractions)
    ])
    
    prompt = f"""As a travel planner, create a detailed itinerary for visiting these attractions:

Attractions List:
{attractions_text}

Trip Details:
- Start Time: {preferences.get('startTime', '9:00 AM')}
- End Time: {preferences.get('endTime', '6:00 PM')}
- Transportation Mode: {preferences.get('transportation', 'walking')}
- Pace: {preferences.get('pace', 'moderate')}

Please create a detailed itinerary that:
1. Includes realistic travel times between locations
2. Suggests a logical order to visit attractions
3. Includes a lunch break around midday
4. Considers the rating of each attraction
5. Provides brief tips for each location
6. Estimates duration at each stop

Format the response as:
TIME - LOCATION (DURATION)
- Brief description or tip
- Travel time to next location

Example:
9:00 AM - Museum of Art (90 minutes)
- Start with the main exhibition hall
- Perfect time to avoid crowds
- 15 min walk to next location"""

    try:
        # Updated OpenAI API call syntax for version 1.0.0+
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced travel planner who creates detailed, practical itineraries."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )
        
        # Updated response parsing
        generated_text = response.choices[0].message.content.strip()
        
        # Format the response
        formatted_response = {
            "itinerary": generated_text,
            "attractions_count": len(attractions),
            "generated_at": datetime.now().isoformat()
        }
        
        return jsonify(formatted_response)
    
    except openai.APIError as e:
        print(f"OpenAI API Error: {str(e)}")
        return jsonify({"error": "OpenAI API error occurred"}), 500
    except openai.RateLimitError:
        return jsonify({"error": "Rate limit exceeded, please try again later"}), 429
    except openai.AuthenticationError:
        return jsonify({"error": "Authentication with OpenAI failed"}), 401
    except Exception as e:
        print(f"Error generating itinerary: {str(e)}")
        return jsonify({"error": "Failed to generate itinerary"}), 500

@app.route('/')
def test():
    return jsonify({"message": "Server is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 