import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from bson.objectid import ObjectId  # Use for generating unique IDs
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

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

def parse_relevant_info(link):
    """
    Removes http/https part from the given link and returns the relevant info.
    :param link: link to be read
    :return cleaned_link: relevant part of the link for remove_duplicates function
    """
    components_list = link.split(':')
    component_1 = components_list[1]
    cleaned_link = component_1[2::]
    return cleaned_link

def remove_duplicates(links):
    """
    Handles issues of having both https and http links for same page by choosing first
    occurrence.
    :param links: Original set of URLs
    :return cleaned_set: cleaned set of URLs
    """
    url_dict = {}
    cleaned_set = set()
    for link in links:
        cleaned_link = parse_relevant_info(link)
        if cleaned_link in url_dict.keys():
            url_dict[cleaned_link] += 1
        else:
            url_dict[cleaned_link] = 1
            cleaned_set.add(link)

    return cleaned_set

# Example usage
if __name__ == "__main__":
    target_url = "https://www.rpi.edu/"

    try:
        load_dotenv()
        # Process the web page
        extracted_urls, page_json = process_web_page(target_url)

        #removing duplicate references
        extracted_urls = remove_duplicates(extracted_urls)

        # Print the extracted URLs
        print("Extracted URLs:")
        for url in extracted_urls:
            print(url)

        # Print the JSON object
        print("\nPage JSON:")
        print(json.dumps(page_json, indent=4))

        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.test
        collection = db.RAW
        print(collection)
        result = collection.find()
        print(result)


    except Exception as e:
        print(str(e))
