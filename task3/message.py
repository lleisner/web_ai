import json
from datetime import datetime
from better_profanity import profanity

class MessageStore:
    def __init__(self, file_path, max_messages):
        self.file_path = file_path
        self.max_messages = max_messages
        self.welcome_message = {
            'content': "Welcome to WeatherChat! 🌍⛅ Discuss the weather worldwide and get real-time updates.",
            'sender': "WeatherBot",
            'timestamp': "0000-00-00T00:00:00Z",
            'extra': None
        }

    def read_messages(self):
        try:
            with open(self.file_path, 'r') as f:
                messages = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            messages = []

        if not messages or messages[0]['content'] != self.welcome_message['content']:
            messages.insert(0, self.welcome_message)
            self.save_messages(messages)

        return messages

    def save_messages(self, messages):
        with open(self.file_path, 'w') as f:
            json.dump(messages, f)

    def add_message(self, content, sender, timestamp, extra=None):
        if profanity.contains_profanity(content):
            return "Message contains banned words"

        messages = self.read_messages()
        messages.append({'content': content, 'sender': sender, 'timestamp': timestamp, 'extra': extra})

        # Ensure message limit
        if len(messages) > self.max_messages:
            messages = [messages[0]] + messages[-(self.max_messages - 1):]

        self.save_messages(messages)
        return "OK"

    def generate_weather_response(self, user_message):
        import random
        import re

        pattern = r"^/weather\s+(.+)"
        match = re.match(pattern, user_message, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            conditions = ["sunny", "cloudy", "rainy", "stormy", "snowy"]
            response_text = f"The current weather in {location} is {random.choice(conditions)}."
            return {'content': response_text, 'sender': "WeatherBot", 'timestamp': datetime.utcnow().isoformat() + "Z", 'extra': None}

        return None
