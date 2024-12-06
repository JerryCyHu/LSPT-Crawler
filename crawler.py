import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from bson.objectid import ObjectId  # Use for generating unique IDs
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from link import Link

def fetch_page_content(url):
    """
    Fetch the content of the web page from the given URL.

    :param url: The URL of the web page
    :return: Tuple containing the HTTP status code and the response content
    """
    response = requests.get(url)
    return response.status_code, response.content


def parse_html_to_soup(html_content):
    """
    Parse HTML content into a BeautifulSoup object.

    :param html_content: The raw HTML content of the page
    :return: BeautifulSoup object
    """
    return BeautifulSoup(html_content, "html.parser")


def get_full_urls(base_url, page_html):
    """
    Extract and return all full URLs from the given page's HTML.

    :param base_url: The base URL of the web page
    :param page_html: Parsed HTML of the web page
    :return: A set of absolute URLs
    """
    urls = set()
    for link in page_html.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])  # Convert relative to absolute
        urls.add(full_url)
    return urls


def format_page_as_json(url, raw_html):
    """
    Format the page content and metadata into a JSON object.

    :param url: The URL of the web page
    :param raw_html: The raw HTML of the web page
    :return: A JSON-formatted dictionary
    """
    object_id = ObjectId()  # Generate a unique ID
    t_type = "html"  # Define the type of document

    json_obj = {
        "_id": str(object_id),
        "url": url,
        "text_length": len(raw_html),
        "text": raw_html,
        "type": t_type
    }
    return json_obj


def process_web_page(url):
    """
    Process a web page by extracting URLs and formatting its raw HTML into JSON.

    :param url: The URL of the web page
    :return: A tuple containing a set of URLs and a JSON-formatted dictionary
    """
    status_code, content = fetch_page_content(url)

    if status_code == 200:
        # Parse the HTML content
        soup = parse_html_to_soup(content)

        # Extract all URLs from the page
        urls = get_full_urls(url, soup)

        # Convert the raw HTML into a prettified text format
        raw_html = soup.prettify()

        # Format the page details into JSON
        json_data = format_page_as_json(url, raw_html)

        return urls, json_data
    else:
        raise Exception(f"Failed to retrieve the page. Status code: {status_code}")
    
def send_analysis(info):
    '''
    info is jason format
    example info: {"url": "www.google.com", "child_nodes": []}
    '''
    url = "http://lspt-link-analysis.cs.rpi.edu:1234/crawling/add_nodes"

    # Sending the POST request
    try:
        response = requests.post(url, json=data)  # Using JSON payload
        # Checking the response
        if response.status_code == 200:
            print("Success:", response.json())  # Print the response data
        else:
            print("Error:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

# Example usage
if __name__ == "__main__":
    target_url = "https://www.rpi.edu/"

    #domain_name: link object
    domain_links = dict()
    root_link = Link(target_url)
    domain_links[root_link.domain_name] = root_link

    try:
        load_dotenv()
        # Process the web page
        extracted_urls, page_json = process_web_page(target_url)

        for url in extracted_urls:
            domain_name = Link.url_to_domain_name(url)
            if domain_name in domain_links.keys():
                link_obj = domain_links[domain_name]
                link_obj.add_url(url)
            else:
                link_obj = Link(url)
                domain_links[domain_name] = link_obj


        # Print the extracted URLs
        print("Extracted URLs:")
        for link in domain_links.values():
            out_links = link.give_out_links()
            print(out_links)

        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.test
        collection = db.RAW
        result = collection.find()
        # #inserting will use:
        # ret = collection.insert_one(page_json)
        # print(ret)

        # print("Stuff in Result")
        # for document in result:
        #     print(document)

        # The URL to send the POST request
        # The data to send as a string (you can adjust this to your use case)
        info = {"url": "www.youtube.com", "child_nodes": ["www.google.com"]}
        send_analysis(info)

    except Exception as e:
        print(str(e))
