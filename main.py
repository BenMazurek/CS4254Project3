from http_client import HttpClient
from http_parser import build_url_params
from crawler import Crawler
import sys


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python3 main.py <username> <password>")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]


    with HttpClient("sprinter2.cs.vt.edu") as http:
        http.send_request("GET", "/accounts/login/", {
            "Connection": "keep-alive"
        })
        res = http.read_response()
        print(res.start_line)
        for key, value in res.headers.items():
            print(f"{key}:{value}")

        print("\n END MESSAGE ONE \n")

        search_string = 'csrfmiddlewaretoken" value="'
        body = res.body.decode()
        token_pos = body.find(search_string) + len(search_string)
        token, _, _ = body[token_pos:].partition('"')


        urlparams = build_url_params({
            "csrfmiddlewaretoken": token,
            "username": username,
            "password": password
        })
        http.send_request("POST", "/accounts/login/", {
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html",
                "Referer": "http://sprinter2.cs.vt.edu/accounts/login/"
        }, body=urlparams)
        res = http.read_response()
        print(res.start_line)
        for key, value in res.headers.items():
            print(f"{key}:{value}")

        crawler = Crawler(http, "/fakebook/")
        crawler.crawl()


