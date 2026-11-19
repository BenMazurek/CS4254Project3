import socket

class HttpMessage:
    def __init__(self, start_line = None, headers = None, body = None):
        self.start_line = start_line
        self.headers = {} if headers is None else headers
        self.body = body


def read_exact(stream, n):
    chunks = bytearray()
    while len(chunks) < n:
        part = stream.read(n - len(chunks))
        if not part:
            raise ValueError(f"Unexpected EOF: expected {n} bytes, got {len(chunks)}")
        chunks.extend(part)
    return bytes(chunks)

def read_message(message):
    result = HttpMessage()
    result.start_line = message.readline().decode().strip()

    # parse header until double crlf
    curr_line = message.readline()
    while curr_line and curr_line != b"\r\n":
        field_line, _, field_value = curr_line.decode().partition(":")
        result.headers[field_line.strip()] = field_value.strip()
        curr_line = message.readline()

    if not curr_line:
        # connection closed before double clrf, this shouldn't happen
        print("oh no!")

    # Body building

    if "Content-Length" in result.headers:
        result.body = message.read_exact(int(result.headers["Content-Length"]))
    
    elif "Transfer-Encoding" in result.headers and result.headers["Transfer-Encoding"] == "chunked":
        body = bytearray()
        while True:
            size_line = message.readline()
            size_hex = size_line.decode("latin-1").split(";", 1)[0].strip()

            chunk_size = int(size_hex, 16)
            # once the last chunk is found, read and discard any trailer headers until a double crlf
            if chunk_size == 0:
                while True:
                    trailer = message.readline()
                    if not trailer or trailer in (b"\r\n", b"\n"):
                        break
                break

            body.extend(read_exact(message, chunk_size))

            # Read until ending crlf
            ending = message.readline()
        result.body = bytes(body)


    return result

def build_request(method, path, headers, body):

    if body:
        headers["Content-Length"] = str(len(body.encode()))

    result = f"{method} {path} HTTP/1.1\r\n"
    for key, value in headers.items():
        result += f"{key}: {value}\r\n"
    result += "\r\n"
    if body: result += body

    return result.encode()


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




if __name__ == "__main__":

    with HttpClient("sprinter2.cs.vt.edu") as http:
        http.send_request("GET", "/accounts/login/", {
            "Connection": "keep-alive"
        })
        res = http.read_response()
        print(res.start_line)
        for key, value in res.headers.items():
            print(f"{key}:{value}")

        print("\n END MESSAGE ONE \n")

        http.send_request("GET", "/accounts/login/", {
            "Connection": "close"
        })
        res = http.read_response()
        print(res.start_line)
        for key, value in res.headers.items():
            print(f"{key}:{value}")




