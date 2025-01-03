import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict

class Crawler:
    """Web crawler that retrieves and indexes HTML pages starting from a given URL.

    Attributes:
        start_url (str): The URL to begin crawling from.
        prefix (str): Base URL prefix to restrict crawling to a specific domain.
        agenda (list): List of URLs to visit.
        visited_urls (set): Set of already visited URLs.
        index (defaultdict): In-memory index mapping words to lists of URLs.
    """

    def __init__(self, start_url: str, prefix: str):
        """Initializes the crawler with a start URL and URL prefix.

        Args:
            start_url (str): The URL to begin crawling from.
            prefix (str): The base URL prefix to restrict crawling to a specific domain.
        """
        self.start_url = start_url
        self.prefix = prefix
        self.agenda = [start_url]
        self.visited_urls = set()
        self.index = defaultdict(list)

    def crawl(self) -> None:
        """Crawls HTML pages starting from the start URL and updates the in-memory index.

        Outputs the in-memory index to a file after crawling for debugging or inspection.

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
                # Validate the URL format
                if not url.startswith(('http://', 'https://')):
                    print(f"Skipping {url} - Invalid URL format.")
                    continue
                r = requests.get(url)
                print(r, r.encoding)
                if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type", ""):
                    print(f"Skipping {url} - Not an HTML page or bad response.")
                    continue

                soup = BeautifulSoup(r.content, 'html.parser')
                self.index_page(url, soup.get_text())
                self.extract_links(soup, url)

            except requests.exceptions.RequestException as e:
                print(f"Network error while processing {url}: {e}")
            except Exception as e:
                print(f"Unexpected error while processing {url}: {e}")

        # Save the index to a file after crawling is complete
        self.save_index_to_file()

    def index_page(self, url: str, text: str) -> None:
        """Indexes the text content of a page.

        Args:
            url (str): The URL of the page.
            text (str): The text content of the page.

        Returns:
            None
        """
        words = text.split()
        for word in words:
            word = word.lower().strip(".,!?\"'()[]")
            self.index[word].append(url)

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

    def search(self, query: list) -> list:
        """Searches for a query in the index.

        Args:
            query (list): A list of words to search for.

        Returns:
            set: A set of URLs that contain all the query words.
        """
        query_words = [word.lower() for word in query]
        if not query_words:
            return set()
        results = set(self.index[query_words[0]])
        for word in query_words[1:]:
            results.intersection_update(self.index[word])
        return list(results)

    def save_index_to_file(self, file_name: str = "index_debug.txt") -> None:
        """Saves the in-memory index to a file for debugging or inspection.

        Args:
            file_name (str): The name of the file to save the index to. Defaults to "index_debug.txt".

        Returns:
            None
        """
        with open(file_name, "w") as f:
            for word, urls in self.index.items():
                f.write(f"{word}: {', '.join(urls)}\n")

if __name__ == "__main__":
    prefix = 'https://vm009.rz.uos.de/crawl/'
    start_url = prefix + 'index.html'

    crawler = Crawler(start_url, prefix)
    crawler.crawl()

    # Example search
    print("Search results for 'platypus':")
    for i, url in enumerate(crawler.search(["platypus"]), 1):
        print(f"{i}. {url}")
