import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, '/home/u045/public_html/test/web_ai/task2/week1')

# Activate the virtual environment
activate_env = os.path.expanduser('/home/u045/public_html/test/web_ai/task2/week1/venv/bin/activate_this.py')
with open(activate_env) as f:
    exec(f.read(), {'__file__': activate_env})

# Import the Flask app
from helpers import FlaskAppHelper
from whoosh_flask_crawler import WhooshHelper

# Initialize Whoosh helper
whoosh_helper = WhooshHelper(store_content=False)

# Initialize Flask app
flask_app = FlaskAppHelper(whoosh_helper)
application = flask_app.app  # WSGI expects `application`
