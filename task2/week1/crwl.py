import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict

prefix = 'https://www.ikw.uni-osnabrueck.de/en/'

start_url = prefix+'home.html'

agenda = [start_url]

while agenda:
    url = agenda.pop()
    print("Get ",url)
    r = requests.get(url)
    print(r, r.encoding)
    if r.status_code == 200:
        print(r.headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        print(soup.find_all('a'))
        