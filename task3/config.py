import os

# Flask settings
SECRET_KEY = os.getenv('SECRET_KEY', 'This is an INSECURE secret!! DO NOT use this in production!!')

# Channel settings
HUB_URL = 'http://localhost:5555'
HUB_AUTHKEY = '1234567890'
CHANNEL_AUTHKEY = '0987654321'
CHANNEL_NAME = "WeatherChat"
CHANNEL_ENDPOINT = "http://localhost:5001"
CHANNEL_TYPE_OF_SERVICE = 'aiweb24:chat'

# Message settings
MAX_MESSAGES = 100
CHANNEL_FILE = 'messages.json'
