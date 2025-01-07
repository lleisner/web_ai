from helpers import WhooshHelper, FlaskAppHelper
from whoosh_flask_crawler import Crawler

prefix = 'https://vm009.rz.uos.de/crawl/'
start_url = prefix + 'index.html'

# Create Whoosh helper
whoosh_helper = WhooshHelper(store_content=True)

# Initialize Crawler
crawler = Crawler(start_url, prefix, whoosh_helper)
crawler.crawl()

# Create Flask app
flask_app = FlaskAppHelper(whoosh_helper)

app = flask_app.app