import requests
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="weather-chat")

def detect_city_name(message):
    """Detects a city name in a user message using OpenStreetMap."""
    words = message.split()
    for word in words:
        try:
            location = geolocator.geocode(word, exactly_one=True, timeout=2)
            if location:
                return location.address.split(",")[0]  # Return city name
        except Exception:
            continue
    return None

def get_lat_lon(city_name):
    """Retrieve latitude and longitude for a given city name using OpenStreetMap's Nominatim API."""
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    
    try:
        response = requests.get(url, headers={"User-Agent": "WeatherChat/1.0"})
        data = response.json()

        if not data:
            return None, None  # City not found

        lat, lon = data[0]["lat"], data[0]["lon"]
        return float(lat), float(lon)

    except Exception as e:
        print(f"Error fetching coordinates for {city_name}: {e}")
        return None, None

def get_weather(lat, lon):
    """Fetch real-time weather data from Open-Meteo for given latitude & longitude."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    try:
        response = requests.get(url)
        data = response.json()

        if "current_weather" not in data:
            return "Weather data is unavailable at the moment."

        weather = data["current_weather"]
        temperature = weather["temperature"]
        wind_speed = weather["windspeed"]
        condition = weather["weathercode"]

        # Basic condition mapping
        condition_mapping = {
            0: "Clear sky ☀️",
            1: "Mainly clear 🌤️",
            2: "Partly cloudy ⛅",
            3: "Overcast ☁️",
            45: "Fog 🌫️",
            48: "Depositing rime fog 🌫️",
            51: "Drizzle (light) 🌦️",
            53: "Drizzle (moderate) 🌧️",
            55: "Drizzle (dense) 🌧️",
            61: "Rain (light) 🌧️",
            63: "Rain (moderate) 🌧️",
            65: "Rain (heavy) 🌧️",
            71: "Snowfall (light) ❄️",
            73: "Snowfall (moderate) ❄️",
            75: "Snowfall (heavy) ❄️",
            95: "Thunderstorm ⛈️",
        }

        condition_text = condition_mapping.get(condition, "Unknown conditions")

        return f"The weather in this location is {temperature}°C, {condition_text}. Wind speed: {wind_speed} km/h."

    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return "Failed to retrieve weather data."

funny_responses = [
    "I have this strange feeling... like you might be curious about the weather. So here it is!",
    "My old sailor instincts are tingling... Here’s the weather for that place you just mentioned!",
    "A sudden shift in the winds tells me you need a weather update. Here you go!",
    "My neural circuits just had a hunch... You need to know the weather!",
    "I sensed a disturbance in the atmosphere. It must mean you need the latest forecast!",
    "The pressure is dropping… I can feel it. Here’s the weather update you secretly wanted!",
    "I just *knew* you wanted this! Maybe I should start reading fortunes instead..."
]