from http_parser import build_request, read_message
import socket

class HttpClient:

    def __init__(self, host):
        self.host = host

    def __enter__(self):
        self._start_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_connection()

    def send_request(self, method, path, headers, body = None):
        headers.setdefault("Host", self.host)
        self.sockfile.write(build_request(method, path, headers, body))
        self.sockfile.flush()

    def read_response(self):
        result = read_message(self.sockfile)
        if result.headers.get("Connection") != "keep-alive":
            self._close_connection()
            self._start_connection()
        return result

    def _start_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, 80))
        self.sockfile = self.sock.makefile("rwb")

    def _close_connection(self):
        self.sockfile.close()
        self.sock.close()
