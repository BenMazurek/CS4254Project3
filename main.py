from http_client import HttpClient
from http_parser import build_url_params
from crawler import Crawler
import sys

# Main method
if __name__ == "__main__":

    # Check for correct command line usage
    if len(sys.argv) < 3:
        print("Usage: python3 main.py <username> <password>")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]

    # Initialize HttpClient object to the fakebook site for use in the crawler
    with HttpClient("sprinter2.cs.vt.edu") as http:

        # keep-alive used in HTTP/1.1
        http.send_request("GET", "/accounts/login/", {
            "Connection": "keep-alive"
        })
        res = http.read_response()

        # Search for and store the CSRF middleware token for use in logging in.
        search_string = 'csrfmiddlewaretoken" value="'
        body = res.body.decode()
        token_pos = body.find(search_string) + len(search_string)
        token, _, _ = body[token_pos:].partition('"')

        # Build the body of the login request
        urlparams = build_url_params({
            "csrfmiddlewaretoken": token,
            "username": username,
            "password": password
        })

        # Build the login request, with specific headers to tell the site we are logging in
        http.send_request("POST", "/accounts/login/", {
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html",
                "Referer": "http://sprinter2.cs.vt.edu/accounts/login/"
        }, body=urlparams)
        res = http.read_response()

        # Initialize the crawler with the logged-in HTTP connection,
        # adding the homepage as the first page in the crawler's queue.
        crawler = Crawler(http, "/fakebook/")

        # While there are queued links or any unfound tokens, process them
        while len(crawler.queue) != 0 and len(crawler.found_flags) < 5:

            # crawlNext() pops the foremost link in the queue and processes it.
            # Any links found on the processed page are also added to the queue for later processing.
            crawler.crawlNext()

        # Once the tokens are found, print them to the console.
        for path in crawler.found_flags:
            print(crawler.found_flags[path].group()[44:108])


