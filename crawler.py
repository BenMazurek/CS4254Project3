from http_client import HttpClient
from http_parser import get_status_code
import re
import time


def search(http_client, start_path):
    visited = set(start_path)
    frontier = set()

    while(True):
        


# Want to rework this

class Crawler:

    def __init__(self, http_client, start_path):
        self.http = http_client
        self.curr_path = start_path
        self.visited = set(start_path)
        self.found_flags = set()

    def crawl(self, path = None):
        path = self.curr_path if not path else path

        if path in self.visited:
            return
        self.visited.add(path)

        self.http.send_request("GET", path, {
            "Connection": "keep-alive"
        })
        res = self.http.read_response()

        status_code = get_status_code(res)

        match status_code:
            case 301 | 302:
                if location := response.headers.get("Location"):
                    path = location.strip().removeprefix("http://sprinter2.cs.vt.edu")
                    crawl(path)
            case 403 | 404:
                pass
            case 500:
                self.visited.remove(path)
                crawl(path)
            case 503:
                time.sleep(0.5)
                self.visited.remove(path)
                crawl(path)
            case 200:
                body = res.body.decode()
                match = re.search(r'class="secret_flag" style="color:red">FLAG: (.{64})<\/h2>')
                if match:
                    #record that the flag is stored

                links = re.findall(r'"\/fakebook\/[a-zA-Z0-9\/\-]+\/"', body)
                for link in links:
                    crawl(link)


def find_links(body):
    matches = re.findall(r"\/fakebook\/\d+\/", body)
    for match in matches:
        print(match)

def handle_redirect(response):
    if location := response.headers.get("Location"):
        path = location.strip().removeprefix("http://sprinter2.cs.vt.edu")
        crawl(path)

def retry_request()




