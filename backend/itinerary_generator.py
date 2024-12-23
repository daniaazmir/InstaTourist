import requests
import os
from datetime import datetime, timedelta

def setup_ai():
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

def generate_itinerary(attractions, preferences):
    headers = setup_ai()
    
    # Limit to top 5 attractions to avoid overwhelming the model
    top_attractions = sorted(attractions, key=lambda x: float(x['rating'] or 0), reverse=True)[:5]
    
    attractions_text = "\n".join([
        f"{i+1}. {a['name']} ({a['rating']}★)"
        for i, a in enumerate(top_attractions)
    ])
    
    prompt = f"""Create a tourist itinerary:

Attractions:
{attractions_text}

Start: {preferences.get('startTime', '9:00 AM')}
End: {preferences.get('endTime', '6:00 PM')}
Transport: {preferences.get('transportation', 'walking')}

Example format:
9:00 AM - First location (60 min)
10:15 AM - Second location (45 min)
12:00 PM - Lunch break (60 min)
1:15 PM - Third location (90 min)"""

    try:
        # Using a smaller, more focused model
        API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_length": 200,
                    "min_length": 50,
                    "temperature": 0.5,
                    "top_k": 30,
                    "do_sample": True,
                    "num_return_sequences": 1
                }
            }
        )
        
        print("API Status Code:", response.status_code)
        print("API Response:", response.text)
        
        if response.status_code != 200:
            print(f"AI API Error: {response.text}")
            return create_fallback_itinerary(attractions, preferences)
        
        result = response.json()
        generated_text = result[0]['generated_text'] if isinstance(result, list) else result['generated_text']
        
        # Clean up and format the response
        cleaned_text = generated_text.replace(prompt, '').strip()
        
        # Stricter validation
        if (len(cleaned_text) < 50 or 
            not all(x in cleaned_text for x in ['AM', 'PM']) or
            cleaned_text.count(':') < 3):
            print("AI response inadequate, using fallback")
            return create_fallback_itinerary(attractions, preferences)
            
        formatted_text = f"""📋 AI-Generated Itinerary
------------------------

{cleaned_text}

💡 Tips for Selected Attractions:
"""
        # Add specific tips for each attraction
        for attr in top_attractions:
            formatted_text += f"\n{attr['name']}:\n"
            formatted_text += f"✓ Rating: {attr['rating']} stars\n"
            if 'museum' in attr['name'].lower():
                formatted_text += "✓ Check exhibition schedule\n"
            elif 'park' in attr['name'].lower():
                formatted_text += "✓ Best visited in good weather\n"
            elif 'temple' in attr['name'].lower() or 'church' in attr['name'].lower():
                formatted_text += "✓ Respect dress codes and customs\n"
            
        print("Successfully generated AI itinerary")
        return formatted_text
        
    except Exception as e:
        print(f"Error with AI generation: {str(e)}")
        return create_fallback_itinerary(attractions, preferences)

def create_fallback_itinerary(attractions, preferences):
    """Create a structured itinerary with realistic timing"""
    start_time = datetime.strptime(preferences.get('startTime', '9:00 AM'), '%I:%M %p')
    end_time = min(
        datetime.strptime(preferences.get('endTime', '6:00 PM'), '%I:%M %p'),
        datetime.strptime('10:00 PM', '%I:%M %p')
    )
    current_time = start_time
    
    # Define minimum durations based on attraction type (you can expand this)
    MIN_DURATION = {
        'museum': 90,      # 1.5 hours minimum for museums
        'park': 60,        # 1 hour minimum for parks
        'temple': 45,      # 45 minutes for temples
        'restaurant': 60,  # 1 hour for restaurants
        'shopping': 60,    # 1 hour for shopping areas
        'default': 45      # 45 minutes default minimum
    }
    
    # Calculate travel time based on transportation mode and rough distance
    def estimate_travel_time(origin, destination, mode):
        # Calculate rough distance using coordinates
        from math import sin, cos, sqrt, atan2, radians
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371  # Earth's radius in kilometers
            
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            return distance
        
        dist = calculate_distance(
            origin['location']['lat'], 
            origin['location']['lng'],
            destination['location']['lat'], 
            destination['location']['lng']
        )
        
        # Estimate travel time based on mode and distance
        speeds = {
            'walking': 5,           # 5 km/h walking speed
            'public_transport': 20, # 20 km/h average with stops
            'driving': 30          # 30 km/h urban average
        }
        
        speed = speeds.get(mode, speeds['walking'])
        time_hours = dist / speed
        return max(10, int(time_hours * 60))  # Minimum 10 minutes, convert to minutes

    # Sort attractions by location to optimize route
    def optimize_route(attractions, start_location=None):
        if not start_location:
            start_location = attractions[0]
        
        route = [start_location]
        remaining = attractions[1:] if attractions[0] == start_location else attractions[:]
        
        while remaining:
            current = route[-1]
            next_stop = min(remaining, key=lambda x: estimate_travel_time(current, x, preferences.get('transportation', 'walking')))
            route.append(next_stop)
            remaining.remove(next_stop)
        
        return route

    # Optimize the route
    optimized_attractions = optimize_route(attractions)
    
    # Calculate available time
    total_minutes = (end_time - start_time).seconds / 60
    lunch_duration = 60
    
    itinerary = ["📋 Your Customized Itinerary\n"]
    itinerary.append("------------------------\n")
    
    # Morning activities
    itinerary.append("🌅 Morning Activities:")
    lunch_added = False
    
    for i, attraction in enumerate(optimized_attractions):
        if current_time >= end_time:
            break
            
        # Check if it's time for lunch (between 12:00 and 14:00)
        current_hour = current_time.hour
        if not lunch_added and current_hour >= 12 and current_hour < 14:
            itinerary.append("\n🍴 Lunch Break:")
            itinerary.append(f"⏰ {current_time.strftime('%I:%M %p')} - Take a refreshing break (60 minutes)")
            current_time += timedelta(minutes=lunch_duration)
            lunch_added = True
            itinerary.append("\n🌇 Afternoon Activities:")
            continue
        
        time_str = current_time.strftime('%I:%M %p')
        
        # Determine minimum duration based on attraction name/description
        name_lower = attraction['name'].lower()
        desc_lower = attraction['description'].lower()
        duration = MIN_DURATION['default']
        
        for key, min_time in MIN_DURATION.items():
            if key in name_lower or key in desc_lower:
                duration = min_time
                break
                
        # Adjust duration based on pace preference
        pace_multiplier = {
            'relaxed': 1.3,
            'moderate': 1.0,
            'fast': 0.8
        }.get(preferences.get('pace'), 1.0)
        
        duration = int(duration * pace_multiplier)
        
        # Add the attraction to itinerary
        itinerary.append(f"\n⏰ {time_str} - {attraction['name'].upper()}")
        itinerary.append(f"📍 {attraction['description']}")
        if attraction['rating']:
            itinerary.append(f"⭐ Rating: {attraction['rating']}")
        itinerary.append(f"⏱️ Duration: {duration} minutes")
        
        current_time += timedelta(minutes=duration)
        
        # Add travel time to next location if not the last attraction
        if i < len(optimized_attractions) - 1:
            travel_time = estimate_travel_time(
                attraction,
                optimized_attractions[i + 1],
                preferences.get('transportation', 'walking')
            )
            itinerary.append(f"🚶 {travel_time} minutes travel to next location")
            current_time += timedelta(minutes=travel_time)
    
    # Add end time
    itinerary.append(f"\n🏁 End of Tour: {min(current_time, end_time).strftime('%I:%M %p')}")
    
    # Add transportation-specific tips
    itinerary.append("\n🚗 Transportation Tips:")
    if preferences.get('transportation') == 'walking':
        itinerary.append("✓ Wear comfortable walking shoes")
        itinerary.append("✓ Bring water and stay hydrated")
        itinerary.append("✓ Consider weather conditions")
    elif preferences.get('transportation') == 'public_transport':
        itinerary.append("✓ Check local transit schedules")
        itinerary.append("✓ Consider getting a day pass")
        itinerary.append("✓ Download local transit app")
    else:  # driving
        itinerary.append("✓ Check parking availability")
        itinerary.append("✓ Consider traffic conditions")
        itinerary.append("✓ Have navigation app ready")
    
    # Add general tips
    itinerary.append("\n💡 General Tips:")
    itinerary.append("✓ Check attraction opening hours")
    itinerary.append("✓ Make reservations if needed")
    itinerary.append("✓ Keep emergency contacts handy")
    
    return "\n".join(itinerary)