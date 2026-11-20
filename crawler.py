# Honor pledge:

# As a Hokie, I, Whit Faughnan (PID: whitfaughnan),  will conduct myself with honor and integrity at all times.  
# I will not lie, cheat, or steal, nor will I accept the actions of those who do.

# As a Hokie, I, Ben Mazurek (PID: benmazurek),  will conduct myself with honor and integrity at all times.  
# I will not lie, cheat, or steal, nor will I accept the actions of those who do.

from http_client import HttpClient
from http_parser import get_status_code
from collections import deque
import re
import time

# Web crawler class. Uses a queue of pending links and a 
# dictionary of previously visited or queued links to visit
# all possible Fakebook pages linked in other Fakebook pages
# without revisiting pages it has already scanned.
class Crawler:

    # Initialization begins by passing the HttpClient
    # object with an open and logged-in connection to Fakebook.
    # The start_path link is the first link added to the queue to
    # be scraped by the webcrawler. Any links it finds on the home
    # page are added to the queue, and additional webpages contribute
    # additional queues.
    def __init__(self, http_client, start_path):
        self.http = http_client
        self.visited = {}
        self.found_flags = {}
        self.queue = deque()
        self.queue.append(start_path)
        self.visited[start_path] = "queued"

    # The crawling function. This function takes the first link in the
    # queue to be scanned, requests that page via the HttpClient self.http,
    # and scrapes the HTML returned by the Fakebook server. If the response
    # code is not 200 OK, other response codes are handled here. 
    # If the crawler finds more links to be scraped, it adds them to its queue,
    # and the next call to crawlNext will scan the first page up next in the queue.
    def crawlNext(self):

        # Get the first link in queue
        path = self.queue.popleft()

        # Mark in the dictionary that this link has been visited
        self.visited[path] = "visited"

        # Request page at the link from fakebook
        # This request allows gzip-encoded webpages to be returned by the server
        self.http.send_request("GET", path, {
            "Connection": "keep-alive",
            "Accept": "text/html",
            "Accept-Encoding": "gzip"
        })

        # Read response
        response = self.http.read_response()

        # Get status code and determine action
        status_code = get_status_code(response)

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

                # Decode the response body and scrape it for a secret flag
                body = response.body.decode()
                match = re.search(r'class="secret_flag" style="color:red">FLAG: (.{64})<\/h2>', body)

                # If a secret flag is found, add the match object to our dictionary of found flags
                if match:
                    self.found_flags[path] = match

                # If any links are found, add them to the queue if they are not
                # already visited or queued to be visited
                links = re.findall(r'\/fakebook\/[a-zA-Z0-9\/\-]+\/', body)
                for link in links:
                    if link not in self.visited:
                        self.visited[link] = "queued"
                        self.queue.append(link)

                return




