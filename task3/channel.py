from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
import logging
from config import *
from message import MessageStore
from better_profanity import profanity
from get_weather import get_lat_lon, get_weather, detect_city_name, funny_responses

# Setup logging
logging.basicConfig(level=logging.INFO)

# Flask setup
app = Flask(__name__)
CORS(app)
app.config.from_object('config')

# Initialize message store
message_store = MessageStore(CHANNEL_FILE, MAX_MESSAGES)

# Authorization decorator
def require_auth(f):
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers or request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
            return "Invalid authorization", 400
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/health', methods=['GET'])
@require_auth
def health_check():
    return jsonify({'name': CHANNEL_NAME}), 200

@app.route('/', methods=['GET'])
@require_auth
def get_messages():
    return jsonify(message_store.read_messages())

@app.route('/', methods=['POST'])
@require_auth
def send_message():
    """Handles incoming messages, applies profanity filter, and generates weather responses."""
    message = request.json
    if not message or 'content' not in message or 'sender' not in message or 'timestamp' not in message:
        return jsonify({"status": "error", "error": "Invalid message format"}), 400

    user_message = message['content'].strip().lower()
    sender = message['sender']

    # **Profanity Check**
    if profanity.contains_profanity(user_message):
        return jsonify({"status": "blocked", "error": "Message contains banned words!"}), 200

    # **Store the User Message**
    response = message_store.add_message(
        message['content'], sender, message['timestamp'], message.get('extra')
    )

    if response != "OK":
        return jsonify({"status": "error", "error": response}), 400
    
    # **Detect City Name & Provide Weather**
    city_name = detect_city_name(user_message)
    
    if city_name:
        lat, lon = get_lat_lon(city_name)

        if lat is None or lon is None:
            bot_response = f"Could not find weather data for '{city_name}'. Try a different city."
        else:
            weather_info = get_weather(lat, lon, city_name)
            bot_response = f"{random.choice(funny_responses)} {weather_info}"

        message_store.add_message(bot_response, "WeatherBot", message['timestamp'])

    return jsonify({"status": "ok"}), 200


@app.route("/check_profanity", methods=["POST"])
def check_profanity():
    data = request.json
    text = data.get("text", "")

    is_profane = profanity.contains_profanity(text)
    return jsonify({"is_profane": is_profane})

# Channel registration
@app.cli.command('register')
def register_channel():
    response = requests.post(
        HUB_URL + '/channels',
        headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
        json={"name": CHANNEL_NAME, "endpoint": CHANNEL_ENDPOINT, "authkey": CHANNEL_AUTHKEY, "type_of_service": CHANNEL_TYPE_OF_SERVICE}
    )

    if response.status_code == 200:
        print("Channel registered successfully!")
    else:
        print(f"Error registering channel: {response.status_code} - {response.text}")


if __name__ == '__main__':
    app.run(port=5001, debug=True)
