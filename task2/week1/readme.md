# Flask Whoosh Web Crawler

This repository contains a Python-based web crawler integrated with a **Whoosh** search engine and a **Flask** web application for searching and retrieving web content. The project demonstrates a combination of web crawling, content indexing, and a search-friendly interface.

## Features
- **Web Crawling**: Extracts HTML content from web pages and indexes it.
- **Content Indexing**: Uses Whoosh to store and manage indexed content for efficient searching.
- **Flask Integration**: A simple Flask-based web app allows users to search indexed content via a browser.
- **Customizable**: Flexible configuration options for the crawling scope, content extraction, and indexing.

## File Structure
- `whoosh_flask_crawler.py`: The main script that:
  - Crawls web pages starting from a given URL.
  - Extracts and indexes content using the `WhooshHelper` class.
  - Runs a Flask app for querying the indexed content.
- `helpers.py`: Contains helper classes:
  - **WhooshHelper**: Manages the Whoosh index, document addition, and search functionality.
  - **FlaskAppHelper**: Handles the Flask app logic for rendering search results.
- `app.py`: Entry point for running the Flask app and crawler.
- `crawler.wsgi`: Configuration for deploying the Flask app using WSGI.
- `crawler.py`: A standalone web crawler prototype without Whoosh or Flask integration.

