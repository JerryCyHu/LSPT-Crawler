import urllib.request

from bs4 import BeautifulSoup
import requests



crawler_frontier = []
robots_store = []


def add_links(URL):
    crawler_frontier.append(URL)




link = "https://www.rpi.edu/"
f = urllib.request.urlopen(link)
myfile = f.read()
#print(myfile)



