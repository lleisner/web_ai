from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer, SimpleAnalyzer
from whoosh import highlight
from flask import Flask, request, render_template
import re
import shutil
import os
import requests
from bs4 import BeautifulSoup


class WhooshHelper:
    """Helper class for managing Whoosh index.

    Attributes:
        index_dir (str): Directory where the Whoosh index is stored.
        store_content (bool): Store full page contents in memory or load on the fly.
        schema (Schema): Schema defining the structure of the index.
        index (whoosh.index.Index): Whoosh index instance.
    """
    def __init__(self, index_dir: str = "indexdir", store_content: bool = True):
        """Initializes the WhooshHelper with an index directory and configuration.

        Args:
            index_dir (str, optional): Directory where the Whoosh index is stored. Defaults to "indexdir".
            store_content (bool, optional): Whether to store full content in the index. Defaults to True.
        """
        self.index_dir = index_dir
        self.store_content = store_content
        self.schema = Schema(
            url=ID(stored=True),
            title=TEXT(stored=True, analyzer=SimpleAnalyzer()),
            content=TEXT(stored=store_content, analyzer=SimpleAnalyzer()),
        )
        self.index = self._get_or_create_index()

    def _get_or_create_index(self):
        """Creates or opens the Whoosh index, resetting if schema mismatch is detected."""
        if os.path.exists(self.index_dir):
            try:
                ix = open_dir(self.index_dir)
                self._check_schema(ix)
                return ix
            except Exception as e:
                print(f"Schema mismatch or corrupted index: {e}")
                print("Resetting the index directory...")
                shutil.rmtree(self.index_dir)
        os.mkdir(self.index_dir)
        return create_in(self.index_dir, self.schema)

    def _check_schema(self, index):
        """Checks whether the existing index schema matches the current configuration.

        Args:
            index: The opened Whoosh index.

        Raises:
            ValueError: If the schema does not match the current configuration.
        """
        existing_schema = index.schema
        if "content" in existing_schema:
            if existing_schema["content"].stored != self.schema["content"].stored:
                raise ValueError("Schema mismatch: 'content' field storage differs.")
        else:
            if self.store_content:
                raise ValueError("Schema mismatch: 'content' field missing in existing schema.")
            
            
    def add_document(self, url: str, title: str, content: str) -> None:
        """Adds a document to the Whoosh index.

        Args:
            url (str): URL of the document.
            title (str): Title of the document.
            content (str): Full content of the document.

        Returns:
            None
        """
        writer = self.index.writer()
        if self.store_content:
            writer.add_document(url=url, title=title, content=content)
        else:
            writer.add_document(url=url, title=title, content=content)
        writer.commit()

    def fetch_page_content(self, url: str) -> str:
        """Fetches the content of a page by its URL.

        Args:
            url (str): The URL of the page.

        Returns:
            str: The cleaned text content of the page.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove unwanted tags and get text
            for tag in soup(['script', 'style']):
                tag.decompose()
            return soup.get_text(strip=True)
        except Exception as e:
            print(f"Failed to fetch content for {url}: {e}")
            return ""
        

    def search(self, query_str: str) -> list:
        """Searches the Whoosh index for the given query string.

        Args:
            query_str (str): The search query string.

        Returns:
            list: A list of dictionaries containing URLs, titles, and relevant descriptions.
        """
        with self.index.searcher() as searcher:
            #parser = MultifieldParser(["title", "content"], self.schema)
            parser = QueryParser("content", self.schema)
            query = parser.parse(query_str)
            
            results = searcher.search(query)

            # Configure highlighter
            results.fragmenter = highlight.ContextFragmenter(surround=40)
            results.formatter = highlight.HtmlFormatter(tagname="b")

            unique_results = {}
            for result in results:
                url = result["url"]
                if url not in unique_results:
                    if self.store_content:
                        # Use stored content for highlighting
                        highlight_result = result.highlights("content")
                    else:
                        # Dynamically fetch content for highlighting
                        content = self.fetch_page_content(url)
                        if content:
                            # Use dynamically fetched content to highlight
                            highlight_result = results.highlighter.highlight_hit(result, "content", text=content)
                        else:
                            highlight_result = "No description available."
                            
                    # Clean up highlight formatting for better display
                    if highlight_result:
                        highlight_result = re.sub(r'<b class="match term\d+">', '<b>', highlight_result)
                        highlight_result = highlight_result.replace('</b>', '</b>')

                    unique_results[url] = {
                        "url": url,
                        "title": result["title"],
                        "description": highlight_result or "No description available."
                    }
            return list(unique_results.values())


    def extract_description(self, content: str, query: str, max_length: int = 200) -> str:
        """Extracts a meaningful description from the content around the query.

        Args:
            content (str): The full text content of the document.
            query (str): The user's search query.
            max_length (int): Maximum length of the description.

        Returns:
            str: A snippet of the content containing the query, or a fallback.
        """

        # Find the query within the content
        query_match = re.search(rf'\b{re.escape(query)}\b', content, re.IGNORECASE)
        if query_match:
            # Extract a snippet around the query match
            start = max(0, query_match.start() - 50)
            end = min(len(content), query_match.end() + 150)
            snippet = content[start:end]
            
            # Add ellipses for context if truncated
            return (("..." if start > 0 else "") + snippet + ("..." if end < len(content) else "")).strip()
        
        # Fallback to the first sentence if the query is not found
        sentences = re.split(r'(?<=[.!?]) +', content)
        return sentences[0][:max_length] + "..." if sentences else "No description available."



class FlaskAppHelper:
    """Helper class for managing the Flask app.

    Attributes:
        app (Flask): Flask application instance.
        whoosh_helper (WhooshHelper): Instance of the WhooshHelper for managing the index.
    """

    def __init__(self, whoosh_helper: WhooshHelper):
        """Initializes the FlaskAppHelper with a WhooshHelper instance.

        Args:
            whoosh_helper (WhooshHelper): Instance of the WhooshHelper for managing the index.
        """
        self.app = Flask(__name__)
        self.whoosh_helper = whoosh_helper

        @self.app.route("/")
        def home():
            """Renders the home page with the search form.

            Returns:
                str: HTML content of the home page.
            """
            return render_template("search_form.html")

        @self.app.route("/search")
        def search():
            """Processes the search query and displays results.

            Returns:
                str: HTML content of the search results page.
            """
            query = request.args.get("q", "")
            results = self.whoosh_helper.search(query)
            return render_template("results.html", results=results)

    def run(self, host: str = "0.0.0.0", port: int = 5000) -> None:
        """Runs the Flask app.

        Args:
            host (str): Host address to run the app on. Defaults to "0.0.0.0".
            port (int): Port number to run the app on. Defaults to 5000.

        Returns:
            None
        """
        self.app.run(host=host, port=port)
        
        

