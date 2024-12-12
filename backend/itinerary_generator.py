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
    
    # Create a more structured attractions list
    attractions_text = "\n".join([
        f"- {a['name']}: {a['description']} (Rating: {a['rating']})"
        for a in attractions
    ])
    
    # Create a more structured prompt
    prompt = f"""Task: Create a detailed travel itinerary.

Attractions Available:
{attractions_text}

Schedule Parameters:
- Start Time: {preferences.get('startTime', '9:00 AM')}
- End Time: {preferences.get('endTime', '6:00 PM')}
- Pace: {preferences.get('pace', 'moderate')}
- Transportation: {preferences.get('transportation', 'walking')}

Please provide a structured itinerary with exact timings."""
    
    try:
        # Using a more sophisticated model
        API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_length": 800,
                    "min_length": 200,
                    "temperature": 0.7,
                    "num_return_sequences": 1
                }
            }
        )
        
        if response.status_code != 200:
            # Fallback to structured itinerary if API fails
            return create_fallback_itinerary(attractions, preferences)
        
        result = response.json()
        generated_text = result[0]['generated_text'] if isinstance(result, list) else result['generated_text']
        
        # Clean up the generated text
        final_text = generated_text.replace(prompt, '').strip()
        
        # If response is too short or contains repetitive content, use fallback
        if len(final_text) < 100 or final_text.count("Museum of the Rockies") > 2:
            return create_fallback_itinerary(attractions, preferences)
            
        return final_text
        
    except Exception as e:
        print(f"Error generating itinerary: {str(e)}")
        return create_fallback_itinerary(attractions, preferences)

def create_fallback_itinerary(attractions, preferences):
    """Create a structured itinerary when AI generation fails"""
    start_time = datetime.strptime(preferences.get('startTime', '9:00 AM'), '%I:%M %p')
    current_time = start_time
    
    # Calculate time per attraction plus travel time
    total_hours = (datetime.strptime(preferences.get('endTime', '6:00 PM'), '%I:%M %p') - start_time).seconds / 3600
    base_time_per_attraction = min(1.5, total_hours / (len(attractions) + 2))  # +2 for lunch and buffer
    travel_time = 20  # minutes between locations
    
    itinerary = ["📋 Your Customized Itinerary\n"]
    itinerary.append("------------------------\n")
    
    # Morning activities
    itinerary.append("🌅 Morning Activities:")
    for i, attraction in enumerate(attractions[:2]):
        time_str = current_time.strftime('%I:%M %p')
        duration = int(base_time_per_attraction * 60)
        
        itinerary.append(f"\n⏰ {time_str} - {attraction['name'].upper()}")
        itinerary.append(f"📍 {attraction['description']}")
        if attraction['rating']:
            itinerary.append(f"⭐ Rating: {attraction['rating']}")
        itinerary.append(f"⏱️ Duration: {duration} minutes")
        
        # Add travel time to next location
        if i < len(attractions[:2]) - 1:
            current_time = (datetime.strptime(time_str, '%I:%M %p') + 
                          timedelta(minutes=duration + travel_time))
            itinerary.append(f"🚶 {travel_time} minutes travel to next location")
        else:
            current_time = (datetime.strptime(time_str, '%I:%M %p') + 
                          timedelta(minutes=duration))
    
    # Lunch break
    lunch_time = max(
        current_time + timedelta(minutes=30),
        datetime.strptime('12:00 PM', '%I:%M %p')
    )
    itinerary.append("\n🍴 Lunch Break:")
    itinerary.append(f"⏰ {lunch_time.strftime('%I:%M %p')} - Take a refreshing break (60 minutes)")
    if preferences.get('pace') == 'relaxed':
        itinerary.append("💡 Tip: Use this time to rest and recharge")
    
    # Afternoon activities
    current_time = lunch_time + timedelta(minutes=60)
    itinerary.append("\n🌇 Afternoon Activities:")
    
    for i, attraction in enumerate(attractions[2:]):
        time_str = current_time.strftime('%I:%M %p')
        duration = int(base_time_per_attraction * 60)
        
        itinerary.append(f"\n⏰ {time_str} - {attraction['name'].upper()}")
        itinerary.append(f"📍 {attraction['description']}")
        if attraction['rating']:
            itinerary.append(f"⭐ Rating: {attraction['rating']}")
        itinerary.append(f"⏱️ Duration: {duration} minutes")
        
        # Add travel time to next location
        if i < len(attractions[2:]) - 1:
            current_time = (datetime.strptime(time_str, '%I:%M %p') + 
                          timedelta(minutes=duration + travel_time))
            itinerary.append(f"🚶 {travel_time} minutes travel to next location")
        else:
            current_time = (datetime.strptime(time_str, '%I:%M %p') + 
                          timedelta(minutes=duration))
    
    # Add pace-specific tips
    itinerary.append("\n💡 Travel Tips:")
    if preferences.get('pace') == 'relaxed':
        itinerary.append("✓ Take your time to enjoy each location")
        itinerary.append("✓ Consider extra breaks between attractions")
    elif preferences.get('pace') == 'moderate':
        itinerary.append("✓ Balance sightseeing with rest periods")
        itinerary.append("✓ Stay flexible with timing")
    else:  # fast pace
        itinerary.append("✓ Prioritize must-see attractions")
        itinerary.append("✓ Consider splitting into smaller groups for efficiency")
    
    # General tips
    itinerary.append("\n🎯 General Tips:")
    itinerary.append("✓ 👟 Wear comfortable walking shoes")
    itinerary.append("✓ 🚰 Carry water and snacks")
    itinerary.append("✓ 🕒 Check attraction opening hours")
    itinerary.append(f"✓ 🚶 {preferences.get('transportation', 'walking').title()} is your main mode of transport")
    
    # Weather-based tips (you could add weather API integration here)
    itinerary.append("\n🌤️ Preparation:")
    itinerary.append("✓ Check weather forecast")
    itinerary.append("✓ Bring umbrella/sunscreen as needed")
    itinerary.append("✓ Carry a portable charger")
    
    return "\n".join(itinerary)