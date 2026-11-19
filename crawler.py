from http_client import HttpClient
import re


class Crawler:

    def __init__(self, http_client, start_path):
        self.http = http_client
        self.curr_path = start_path
        self.visited = [start_path]

    def crawl(self):
        self.http.send_request("GET", self.curr_path, {
            "Connection": "keep-alive"
        })
        res = self.http.read_response()
        find_links(res.body.decode())


def find_links(body):
    matches = re.findall(r"\/fakebook\/\d+\/", body)
    for match in matches:
        print(match)
