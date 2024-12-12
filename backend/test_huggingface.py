import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_token():
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    # Test with GPT-2
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    
    test_prompt = """Create a simple travel itinerary for:
    - Museum (Rating: 4.5)
    - Park (Rating: 4.0)
    
    Start time: 9:00 AM
    End time: 2:00 PM"""
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "inputs": test_prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "num_return_sequences": 1
            }
        }
    )
    
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    
    if response.status_code == 200:
        result = response.json()
        print("\nGenerated Text:")
        print(result[0]['generated_text'] if isinstance(result, list) else result['generated_text'])

if __name__ == "__main__":
    test_token() 