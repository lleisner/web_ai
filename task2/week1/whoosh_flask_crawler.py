import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from helpers import FlaskAppHelper, WhooshHelper
import re



class Crawler:
    """Web crawler with Whoosh index integration.

    Attributes:
        start_url (str): The URL to begin crawling from.
        prefix (str): Base URL prefix to restrict crawling to a specific domain.
        agenda (list): List of URLs to visit.
        visited_urls (set): Set of already visited URLs.
        whoosh_helper (WhooshHelper): Instance of the WhooshHelper for managing the index.
    """

    def __init__(self, start_url: str, prefix: str, whoosh_helper: WhooshHelper):
        """Initializes the crawler with a start URL, prefix, and WhooshHelper.

        Args:
            start_url (str): The URL to begin crawling from.
            prefix (str): The base URL prefix to restrict crawling to a specific domain.
            whoosh_helper (WhooshHelper): Instance of the WhooshHelper for managing the index.
        """
        self.start_url = start_url
        self.prefix = prefix
        self.agenda = [start_url]
        self.visited_urls = set()
        self.whoosh_helper = whoosh_helper

    def crawl(self) -> None:
        """Crawls HTML pages starting from the start URL and indexes their content.

        Returns:
            None
        """
        while self.agenda:
            url = self.agenda.pop()
            if url in self.visited_urls:
                continue
            print(f"Get {url}")
            self.visited_urls.add(url)

            try:
                r = requests.get(url)
                if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type", ""):
                    print(f"Skipping {url} - Not an HTML page or bad response.")
                    continue

                soup = BeautifulSoup(r.content, 'html.parser')
                title = soup.title.string if soup.title else "No Title"
                text = soup.get_text()

                self.index_page(url, title, text)
                self.extract_links(soup, url)

            except requests.exceptions.RequestException as e:
                print(f"Network error while processing {url}: {e}")
            except Exception as e:
                print(f"Unexpected error while processing {url}: {e}")

    def index_page(self, url: str, title: str, text: str) -> None:
        """Indexes the page using the Whoosh helper.

        Args:
            url (str): The URL of the page.
            title (str): The title of the page.
            text (str): The text content of the page.

        Returns:
            None
        """
        self.whoosh_helper.add_document(url=url, title=title, content=text)

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> None:
        """Extracts internal links from a page and adds them to the agenda for crawling.

        Args:
            soup (BeautifulSoup): BeautifulSoup object of the page's HTML content.
            base_url (str): The base URL of the current page.

        Returns:
            None
        """
        for link in soup.find_all("a", href=True):
            full_url = urljoin(base_url, link["href"])
            if full_url.startswith(self.prefix) and full_url not in self.visited_urls:
                self.agenda.append(full_url)
                
def extract_main_content(soup: BeautifulSoup) -> str:
    """Extracts the main content from the page using heuristics.

    Args:
        soup (BeautifulSoup): Parsed HTML content of the page.

    Returns:
        str: The main content text.
    """
    # Remove unwanted tags like script, style, nav, and footer
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()

    # Collect text from <p> and <div> tags
    content_blocks = []
    for tag in soup.find_all(['p', 'div']):
        text = tag.get_text(strip=True)
        # Ignore very short or non-alphanumeric-heavy blocks
        if len(text) > 30 and sum(c.isalnum() for c in text) / len(text) > 0.5:
            content_blocks.append(text)
    
    return " ".join(content_blocks)




if __name__ == "__main__":
    prefix = 'https://vm009.rz.uos.de/crawl/'
    start_url = prefix + 'index.html'

    # Create Whoosh helper
    whoosh_helper = WhooshHelper(store_content=False)

    # Initialize Crawler
    crawler = Crawler(start_url, prefix, whoosh_helper)
    crawler.crawl()

    # Run Flask app
    flask_app = FlaskAppHelper(whoosh_helper)
    flask_app.run()
