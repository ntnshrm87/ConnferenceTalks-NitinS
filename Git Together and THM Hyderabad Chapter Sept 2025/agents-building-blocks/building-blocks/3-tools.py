"""
Tools: Enables agents to execute specific actions in external systems.
This component provides the capability to make API calls, database updates, file operations, and other practical actions.


More info: https://platform.openai.com/docs/guides/function-calling?api-mode=responses
"""

import json
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv("../../../.env")


def get_weather(latitude, longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]["temperature_2m"]


def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    raise ValueError(f"Unknown function: {name}")


def get_perplexity_client():
    """Initialize and return Perplexity client"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your-perplexity-api-key-here":
        raise ValueError("PERPLEXITY_API_KEY not found or not set properly")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

def intelligence_with_tools(prompt: str) -> str:
    """
    Simplified tool usage with Perplexity API.
    Detects if weather is needed and fetches it, then provides informed response.
    """
    client = get_perplexity_client()
    
    # Step 1: Check if weather information is needed
    if any(word in prompt.lower() for word in ["weather", "temperature", "paris", "london", "tokyo"]):
        # Default coordinates for common cities
        city_coords = {
            "paris": (48.8566, 2.3522),
            "london": (51.5074, -0.1278),
            "tokyo": (35.6762, 139.6503),
            "default": (48.8566, 2.3522)  # Paris as default
        }
        
        # Simple city detection
        coords = city_coords["default"]
        for city, coord in city_coords.items():
            if city in prompt.lower():
                coords = coord
                break
        
        # Get weather data
        try:
            temperature = get_weather(coords[0], coords[1])
            enhanced_prompt = f"{prompt}\n\nCurrent temperature at the location: {temperature}°C"
        except Exception:
            enhanced_prompt = f"{prompt}\n\nNote: Weather data temporarily unavailable"
    else:
        enhanced_prompt = prompt
    
    # Step 2: Get response from Perplexity
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that can provide information including weather data when available."},
            {"role": "user", "content": enhanced_prompt}
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    result = intelligence_with_tools(prompt="What's the weather like in Paris today?")
    print("Tool Calling Output:")
    print(result)
