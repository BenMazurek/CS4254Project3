
Whit Faughnan, Ben Mazurek
CS4254 Project Group 9
Project 3: Fakebook Web Crawler

Our approach for this project was an object-oriented one. Ben wrote the HttpClient and HttpParser classes
to work with one another to send, receive, and decode the HTTP messages sent and received from the Fakebook
server. These classes also handled cookies, both retreiving the login cookie and keeping that login cookie
for every subsequent request made to the server, that way the web crawler could stay logged in. The Crawler
class was a collaborative effort between Ben and Whit, with Ben's initial recursive implementation eventually
being rewritten by Whit into an implementation based on a queue of upcoming webpages to be scanned and a 
dictionary of queued and scanned pages.

For the main loop and crawler, Ben began with a recursive crawler design, recalling the crawl function whenever
a new list of links was found in a webpage. This caused python to run out of stack memory. To fix this, Whit rewrote
the crawl function into the crawlNext function, while updating the crawler to keep a queue of webpages that had yet to
be scraped, and a dictionary to keep track of webpages that were queued for scraping or had already been visited. By doing this,
the main loop could call the crawlNext function until the crawler had exhausted all the unique reachable Fakebook pages. Alternatively,
the main loop also stops whenever 5 secret tokens have been found, which drastically decreases the runtime of the scraper.

The main challenges of this project came from parsing the HTTP responses for cookies, logging into Fakebook and 
staying logged in, and implementing the scraper in a way that would not exhaust memory. 

The code was tested by initially printing every request sent to the server, and printing every response code received
from the server. This quickly led us to fix any issues with HTTP formatting, as the server would send code 400 if our
requests were not formatted correctly. In addition, printing the HTML body of the HTTP responses helped us to develop
regexes to scan for links and find the secret flags in each webpage scanned by the crawler.