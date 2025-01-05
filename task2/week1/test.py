from flask import Flask

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/u045/test/web_ai/task2/week1'

@app.route("/")
def home():
    return "Hello, World! This is a test Flask app running on Apache2."

