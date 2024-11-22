from bs4 import BeautifulSoup
import requests


url = 'https://www.rpi.edu/'  
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    print(soup.prettify())
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")