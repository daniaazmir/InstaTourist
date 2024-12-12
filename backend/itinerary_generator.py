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
    end_time = min(
        datetime.strptime(preferences.get('endTime', '6:00 PM'), '%I:%M %p'),
        datetime.strptime('10:00 PM', '%I:%M %p')  # Maximum limit of 10 PM
    )
    current_time = start_time
    
    # Calculate available time and time per attraction
    total_minutes = (end_time - start_time).seconds / 60
    num_attractions = len(attractions)
    
    # Reserve time for lunch (60 mins) and travel between locations
    lunch_duration = 60
    travel_time = 20  # minutes between locations
    total_travel_time = (num_attractions - 1) * travel_time
    
    # Calculate time per attraction, ensuring we don't exceed end time
    available_time = total_minutes - lunch_duration - total_travel_time
    time_per_attraction = min(90, int(available_time / num_attractions))  # max 90 mins per attraction
    
    itinerary = ["📋 Your Customized Itinerary\n"]
    itinerary.append("------------------------\n")
    
    # Morning activities
    morning_attractions = [a for a in attractions if current_time.hour < 12]
    itinerary.append("🌅 Morning Activities:")
    for i, attraction in enumerate(morning_attractions):
        if current_time >= end_time:
            break
            
        time_str = current_time.strftime('%I:%M %p')
        duration = min(
            time_per_attraction,
            int((end_time - current_time).seconds / 60)
        )
        
        itinerary.append(f"\n⏰ {time_str} - {attraction['name'].upper()}")
        itinerary.append(f"📍 {attraction['description']}")
        if attraction['rating']:
            itinerary.append(f"⭐ Rating: {attraction['rating']}")
        itinerary.append(f"⏱️ Duration: {duration} minutes")
        
        # Add travel time to next location
        next_time = current_time + timedelta(minutes=duration)
        if i < len(morning_attractions) - 1 and next_time < end_time:
            itinerary.append(f"🚶 {travel_time} minutes travel to next location")
            current_time = next_time + timedelta(minutes=travel_time)
        else:
            current_time = next_time
    
    # Lunch break around noon
    lunch_time = max(
        current_time,
        datetime.strptime('12:00 PM', '%I:%M %p')
    )
    if lunch_time < end_time:
        itinerary.append("\n🍴 Lunch Break:")
        itinerary.append(f"⏰ {lunch_time.strftime('%I:%M %p')} - Take a refreshing break (60 minutes)")
        current_time = lunch_time + timedelta(minutes=lunch_duration)
    
    # Afternoon activities
    if current_time < end_time:
        afternoon_attractions = [a for a in attractions if a not in morning_attractions]
        itinerary.append("\n🌇 Afternoon Activities:")
        
        for i, attraction in enumerate(afternoon_attractions):
            if current_time >= end_time:
                break
                
            time_str = current_time.strftime('%I:%M %p')
            duration = min(
                time_per_attraction,
                int((end_time - current_time).seconds / 60)
            )
            
            itinerary.append(f"\n⏰ {time_str} - {attraction['name'].upper()}")
            itinerary.append(f"📍 {attraction['description']}")
            if attraction['rating']:
                itinerary.append(f"⭐ Rating: {attraction['rating']}")
            itinerary.append(f"⏱️ Duration: {duration} minutes")
            
            # Add travel time to next location
            next_time = current_time + timedelta(minutes=duration)
            if i < len(afternoon_attractions) - 1 and next_time < end_time:
                itinerary.append(f"🚶 {travel_time} minutes travel to next location")
                current_time = next_time + timedelta(minutes=travel_time)
            else:
                current_time = next_time
    
    # Add end time
    itinerary.append(f"\n🏁 End of Tour: {min(current_time, end_time).strftime('%I:%M %p')}")
    
    # Add tips section
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
    
    return "\n".join(itinerary)