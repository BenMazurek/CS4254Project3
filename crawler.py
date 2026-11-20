from http_client import HttpClient
from http_parser import get_status_code
from collections import deque
import re
import time


#def search(http_client, start_path):
#    visited = set(start_path)
#    frontier = set()
#
#    while(True):

# Want to rework this

class Crawler:

    def __init__(self, http_client, start_path):
        self.http = http_client
        self.visited = {}
        self.found_flags = {}
        self.queue = deque()
        self.queue.append(start_path)
        self.visited[start_path] = "queued"

    def crawlNext(self):

        path = self.queue.popleft()

        self.visited[path] = "visited"

        # Request given path from fakebook
        # for cookie in self.http.cookies:

        self.http.send_request("GET", path, {
            "Connection": "keep-alive",
            "Accept": "text/html",
            "Accept-Encoding": "gzip"
        })

        # Read response
        response = self.http.read_response()

        # Get status code and determine action
        status_code = get_status_code(response)

        #breakpoint()
        match status_code:
            case 301 | 302: # Permanently moved
                if location := response.headers.get("Location"):
                    path = location.strip().removeprefix("http://sprinter2.cs.vt.edu")
                    self.visited[path] = "queued"
                    self.queue.append(path)
                    return
            case 403 | 404: # Not found
                pass
            case 500: # Try again
                self.visited[path] = "queued"
                self.queue.append(path)
                return
            case 503: # Back off, rate limited
                time.sleep(0.5)
                self.visited[path] = "queued"
                self.queue.append(path)
                return
            case 200: # OK
                body = response.body.decode()
                match = re.search(r'class="secret_flag" style="color:red">FLAG: (.{64})<\/h2>', body)
                if match:
                    self.found_flags[path] = match

                links = re.findall(r'\/fakebook\/[a-zA-Z0-9\/\-]+\/', body)
                for link in links:
                    if link not in self.visited:
                        self.visited[link] = "queued"
                        self.queue.append(link)

                return

def find_links(body):
    matches = re.findall(r"\/fakebook\/\d+\/", body)
    for match in matches:
        print(match)

def handle_redirect(response):
    if location := response.headers.get("Location"):
        path = location.strip().removeprefix("http://sprinter2.cs.vt.edu")
        crawl(path)

# def retry_request()




