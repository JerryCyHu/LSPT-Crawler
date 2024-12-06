from urllib.parse import urlparse
import urllib.robotparser

class Link:
    def __init__(self, url):
        self.domain_name = self.url_to_domain_name(url)
        self.child_links = dict()
        self.supports_https = self.is_https(url)
        if self.supports_https:
            self.url = f"https://{self.domain_name}"
        else:
            self.url = f"http://{self.domain_name}"
        self.set_robots_parser()
        self.add_url(url)

    @staticmethod
    def is_https(url):
        components = url.split(":")
        if len(components[0]) == 5:
            return True
        return False

    @staticmethod
    def url_to_domain_name(url) -> str:
        # Parse the URL
        parsed_url = urlparse(url)
        # Extract the domain name
        domain_name = parsed_url.netloc
        return domain_name

    def set_robots_parser(self):
        #rp = urllib.robotparser.RobotFileParser()
        #rp.set_url(f"{self.url}/robots.txt")
        #rp.read()
        pass

    def check_robots(self, sub_url) -> bool:
        #tldr
        return True

    def add_url(self, url):
        if url not in self.child_links:
            if self.check_robots(url):
                self.child_links[url] = 1
        else:
            self.child_links[url] += 1

    def give_out_links(self):
        return list(self.child_links.keys())





