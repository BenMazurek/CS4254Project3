# Honor pledge:

# As a Hokie, I, Whit Faughnan (PID: whitfaughnan),  will conduct myself with honor and integrity at all times.  
# I will not lie, cheat, or steal, nor will I accept the actions of those who do.

# As a Hokie, I, Ben Mazurek (PID: benmazurek),  will conduct myself with honor and integrity at all times.  
# I will not lie, cheat, or steal, nor will I accept the actions of those who do.

from http_parser import build_request, read_message
import socket

# HTTP Client class. Stores the hostname we are connecting to,
# in this case sprinter2.cs.vt.edu, the socket in self.sockfile, 
# and stores the cookies so that they are always retransmitted to 
# Fakebook along with any requests.
class HttpClient:

    def __init__(self, host):
        self.host = host
        self.cookies = {}

    def __enter__(self):
        self._start_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_connection()

    # Sends an HTTP request over the socket, including
    # any cookies received previously from Fakebook.
    def send_request(self, method, path, headers, body = None):
        headers.setdefault("Host", self.host)
        if self.cookies:
            cookie_str = "; ".join([f"{name}={cookie}" for name, cookie in self.cookies.items()])
            headers.setdefault("Cookie", cookie_str)
        
        request = build_request(method, path, headers, body)

        self.sockfile.write(request)
        self.sockfile.flush()

    # Reads an HTTP response from the Fakebook server.
    # Any included cookies under the Set-Cookie header field
    # are stored in the self.cookies dictionary to be sent
    # back when any requests are made.
    def read_response(self):
        result = read_message(self.sockfile)
        if result.headers.get("Connection") != "keep-alive":
            self._close_connection()
            self._start_connection()
        if "Set-Cookie" in result.headers:
            for cookie in result.headers["Set-Cookie"]:
                name, found_name, remaining = cookie.partition("=")
                if name and found_name and remaining:
                    value = remaining.partition("; ")[0].strip()
                    name = name.strip()
                    if name and value:
                        self.cookies[name] = value

        return result
    
    # Open an HTTP connection with the webserver at the hostname
    # specified in self.host
    def _start_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, 80))
        self.sockfile = self.sock.makefile("rwb")

    # Close an HTTP connection
    def _close_connection(self):
        self.sockfile.close()
        self.sock.close()
