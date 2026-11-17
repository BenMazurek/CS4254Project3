import socket 

class HttpMessage:
    def __init__(self, start_line = None, headers = {}, body = None):
        self.start_line = start_line
        self.headers = headers
        self.body = body


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
        result.body = message.read(result.headers["Content-Length"])
    
    elif "Transfer-Encoding" in result.headers 
        and result.headers["Transfer-Encoding"] == "chunked":
        # Parse a chunked body


    return result

def build_request(method, path, headers, body = None):
    result = f"{method} {path} HTTP/1.1\r\n"
    for key, value in headers.items():
        result += f"{key}: {value}\r\n"
    result += "\r\n"
    if body: result += body
    return result.encode()


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("sprinter2.cs.vt.edu", 80))
        sock.sendall(build_request("GET", "/accounts/login/", {
            "Host": "sprinter2.cs.vt.edu",
            "Connection": "close"
        }))

        with sock.makefile("rb") as file:
            res = read_message(file)
            print(res.start_line)
            for key, value in res.headers.items():
                print(f"{key}:{value}")
            print(res.body)

