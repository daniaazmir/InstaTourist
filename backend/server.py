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
from functools import lru_cache

app = Flask(__name__)
CORS(app)

# Look for .env file in the parent directory (root of project)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
ACCUWEATHER_API_KEY = os.getenv('ACCUWEATHER_API_KEY')

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Add this near the top of your file, after setting the API keys
if not GOOGLE_PLACES_API_KEY or not openai.api_key:
    print("Warning: Missing API keys!")
    print("GOOGLE_PLACES_API_KEY:", "Present" if GOOGLE_PLACES_API_KEY else "Missing")
    print("OPENAI_API_KEY:", "Present" if openai.api_key else "Missing")

# Cache the weather data for 1 hour
@lru_cache(maxsize=100)
def get_cached_weather(latitude, longitude, timestamp):
    if not ACCUWEATHER_API_KEY:
        raise Exception("AccuWeather API key not configured")
        
    try:
        # First, get the location key using coordinates
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
        location_params = {
            'apikey': ACCUWEATHER_API_KEY,
            'q': f"{latitude},{longitude}",
        }
        
        location_response = requests.get(location_url, params=location_params)
        if location_response.status_code != 200:
            raise Exception(f"AccuWeather API error: {location_response.text}")
            
        location_data = location_response.json()
        if 'Key' not in location_data:
            raise Exception("Location key not found in response")
            
        location_key = location_data['Key']
        
        # Then, get the forecast
        forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"  # Changed to 5-day forecast
        forecast_params = {
            'apikey': ACCUWEATHER_API_KEY,
            'metric': 'true'
        }
        
        forecast_response = requests.get(forecast_url, params=forecast_params)
        if forecast_response.status_code != 200:
            raise Exception(f"Forecast API error: {forecast_response.text}")
            
        forecast_data = forecast_response.json()
        if 'DailyForecasts' not in forecast_data:
            raise Exception("Forecast data not available")
            
        # Add this before formatting the forecast
        print("Raw forecast data:", forecast_data)  # Debug log
        
        # Format the response
        formatted_forecast = []
        for day in forecast_data['DailyForecasts']:
            formatted_forecast.append({
                'date': day['Date'],
                'min_temp': day['Temperature']['Minimum']['Value'],
                'max_temp': day['Temperature']['Maximum']['Value'],
                'day_condition': day['Day']['IconPhrase'],
                'night_condition': day['Night']['IconPhrase'],
                'precipitation_probability': max(
                    day['Day'].get('PrecipitationProbability', 0),
                    day['Night'].get('PrecipitationProbability', 0)
                ),
            })
            
            # And add this after formatting each day
            print(f"Formatted day data: {formatted_forecast[-1]}")  # Debug log
            
        return jsonify({
            'location': location_data['LocalizedName'],
            'country': location_data['Country']['LocalizedName'],
            'forecast': formatted_forecast
        })
        
    except Exception as e:
        raise Exception(f"Failed to fetch weather data: {str(e)}")

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
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not attractions:
        return jsonify({"error": "No attractions provided"}), 400

    # Get weather forecast
    try:
        # Use the existing weather function
        weather_response = get_cached_weather(
            round(latitude, 4), 
            round(longitude, 4), 
            datetime.now().replace(minute=0, second=0, microsecond=0)
        )
        weather_data = weather_response.get_json()  # Convert response to JSON
    except Exception as e:
        print(f"Warning: Could not fetch weather data: {e}")
        weather_data = None

    # Create weather information text
    weather_text = ""
    if weather_data and 'forecast' in weather_data:
        weather_text = "\nWeather Forecast:\n"
        for day in weather_data['forecast']:
            date = datetime.fromisoformat(day['date'].replace('Z', '+00:00')).strftime('%A')
            weather_text += f"- {date}: {day['day_condition']}, {day['min_temp']}°C to {day['max_temp']}°C\n"

    # Create attractions text
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

{weather_text}

Please create a weather-aware itinerary that:
1. Considers the weather forecast when scheduling outdoor vs indoor activities
2. Includes realistic travel times between locations
3. Suggests a logical order to visit attractions
4. Includes a lunch break around midday
5. Considers the rating of each attraction
6. Provides brief tips for each location
7. Estimates duration at each stop
8. Suggests indoor alternatives or timing adjustments based on weather

Format the response as:
TIME - LOCATION (DURATION)
- Weather consideration
- Brief description or tip
- Travel time to next location

Example:
9:00 AM - Indoor Museum (90 minutes)
- Perfect for the morning rain
- Start with the main exhibition hall
- 15 min walk to next location"""

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced travel planner who creates detailed, practical itineraries with weather considerations."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )
        
        generated_text = response.choices[0].message.content.strip()
        
        formatted_response = {
            "itinerary": generated_text,
            "attractions_count": len(attractions),
            "generated_at": datetime.now().isoformat(),
            "weather_included": weather_data is not None
        }
        
        return jsonify(formatted_response)
    
    except Exception as e:
        print(f"Error generating itinerary: {str(e)}")
        return jsonify({"error": "Failed to generate itinerary"}), 500

@app.route('/api/weather/<float:latitude>/<float:longitude>')
def get_weather_forecast(latitude, longitude):
    # Round coordinates to 4 decimal places to improve cache hits
    lat = round(latitude, 4)
    lon = round(longitude, 4)
    
    # Round timestamp to hours to cache for 1 hour
    timestamp = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    try:
        return get_cached_weather(lat, lon, timestamp)
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def test():
    return jsonify({"message": "Server is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 