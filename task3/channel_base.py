## channel.py - a simple message channel with message limiting, banned words filtering,
## and simple active responses for weather queries.
##

from flask import Flask, request, render_template, jsonify
import json
import requests
import re
import random
from datetime import datetime
from better_profanity import profanity

# Load default banned words from better_profanity
profanity.load_censor_words()

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')
app.app_context().push()  # create an app context before initializing db

HUB_URL = 'http://localhost:5555'
HUB_AUTHKEY = '1234567890'
CHANNEL_AUTHKEY = '0987654321'
CHANNEL_NAME = "WeatherChat"  # Updated channel name to reflect the topic
CHANNEL_ENDPOINT = "http://localhost:5001"  # don't forget to adjust in the bottom of the file
CHANNEL_FILE = 'messages.json'
CHANNEL_TYPE_OF_SERVICE = 'aiweb24:chat'

# Maximum number of messages to keep (including the welcome message)
MAX_MESSAGES = 100

@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT
    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
                                "name": CHANNEL_NAME,
                                "endpoint": CHANNEL_ENDPOINT,
                                "authkey": CHANNEL_AUTHKEY,
                                "type_of_service": CHANNEL_TYPE_OF_SERVICE,
                             }))
    if response.status_code != 200:
        print("Error creating channel: " + str(response.status_code))
        print(response.text)
        return

def check_authorization(request):
    global CHANNEL_AUTHKEY
    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        return False
    return True

def check_authorization(request):
    # Temporarily disable authentication for testing purposes
    return True


@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name': CHANNEL_NAME}), 200

# GET: Return list of messages
@app.route('/', methods=['GET'])
def home_page():
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify(read_messages())

# POST: Send a message
@app.route('/', methods=['POST'])
def send_message():
    if not check_authorization(request):
        return "Invalid authorization", 400
    message = request.json
    if not message:
        return "No message", 400
    # Check that required fields are present
    for field in ['content', 'sender', 'timestamp']:
        if field not in message:
            return f"No {field}", 400
    extra = message.get('extra', None)
    
    # Use better_profanity to filter banned words
    if profanity.contains_profanity(message['content']):
        return "Message contains banned words", 400
    
    messages = read_messages()
    
    # Append the user's message
    messages.append({
        'content': message['content'],
        'sender': message['sender'],
        'timestamp': message['timestamp'],
        'extra': extra,
    })
    
    # Trigger an active weather response if applicable (avoid recursion if sender is WeatherBot)
    if message['sender'] != "WeatherBot":
        active_response = generate_weather_response(message['content'])
        if active_response:
            messages.append(active_response)
    
    # Limit messages to the latest MAX_MESSAGES (always preserve the welcome message)
    if len(messages) > MAX_MESSAGES:
        welcome = messages[0]
        # Keep welcome message and the last (MAX_MESSAGES - 1) messages
        messages = [welcome] + messages[-(MAX_MESSAGES - 1):]
    
    save_messages(messages)
    return "OK", 200

# Welcome message (always first)
WELCOME_MESSAGE = {
    'content': "Welcome to WeatherChat! 🌍⛅ Discuss the weather worldwide and get real-time updates. "
               "Whether it's rain, shine, or snow—we've got you covered!",
    'sender': "WeatherBot",
    'timestamp': "0000-00-00T00:00:00Z",
    'extra': None
}

def read_messages():
    global CHANNEL_FILE
    try:
        with open(CHANNEL_FILE, 'r') as f:
            messages = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        messages = []
    # Ensure the welcome message is always the first entry
    if not messages or messages[0]['content'] != WELCOME_MESSAGE['content']:
        messages.insert(0, WELCOME_MESSAGE)
        save_messages(messages)
    return messages

def save_messages(messages):
    global CHANNEL_FILE
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)

# Utility: get current UTC timestamp in ISO format
def get_current_timestamp():
    return datetime.utcnow().isoformat() + "Z"

# Active response generator: if a message starts with "/weather <location>",
# generate a WeatherBot response with a random weather condition.
def generate_weather_response(user_message):
    pattern = r"^/weather\s+(.+)"
    match = re.match(pattern, user_message, re.IGNORECASE)
    if match:
        location = match.group(1).strip()
        conditions = ["sunny", "cloudy", "rainy", "stormy", "snowy"]
        condition = random.choice(conditions)
        response_text = f"The current weather in {location} is {condition}."
        return {
            'content': response_text,
            'sender': "WeatherBot",
            'timestamp': get_current_timestamp(),
            'extra': None
        }
    return None

# Start development web server
if __name__ == '__main__':
    app.run(port=5001, debug=True)
