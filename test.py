import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "http://www.rpi.edu/"
response = requests.get(url)

# Parse HTML
soup = BeautifulSoup(response.content, "html.parser")

def get_full_urls(base_url, page_html):
    """
    Extract and return all full URLs from the given page's HTML.

    :param base_url: The base URL of the web page
    :param page_html: Parsed HTML of the web page
    :return: A list of absolute URLs
    """
    urls = set()
    for link in page_html.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])  # Convert relative to absolute
        urls.add(full_url)
    return urls

# Get all URLs from the page
urls = get_full_urls(url, soup)

# Print each URL
for full_url in urls:
    print(full_url)