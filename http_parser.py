import gzip

# A class for storing different parts of an HTTP message. 
# Optionally, this class can be initialized with a given start line,
# set of headers, and message body. 
class HttpMessage:
    def __init__(self, start_line = None, headers = None, body = None):
        self.start_line = start_line
        self.headers = {} if headers is None else headers
        self.body = body

# Reads an exact length of characters from a bytestream or string,
# and converts that character string to a byte array.
def read_exact(stream, n):
    chunks = bytearray()
    while len(chunks) < n:
        part = stream.read(n - len(chunks))
        if not part:
            raise ValueError(f"Unexpected EOF: expected {n} bytes, got {len(chunks)}")
        chunks.extend(part)
    return bytes(chunks)

# Reads an HTTP response, storing the start line, included headers,
# and message body 
def read_message(message):
    result = HttpMessage()
    result.start_line = message.readline().decode().strip()

    # parse header until double crlf
    curr_line = message.readline()
    while curr_line and curr_line != b"\r\n":
        field_line, _, field_value = curr_line.decode().partition(":")
        field_line = field_line.strip()
        field_value = field_value.strip()
        if field_line == "Set-Cookie":
            result.headers.setdefault("Set-Cookie", [])
            result.headers[field_line].append(field_value)
        else:
            result.headers[field_line] = field_value
        curr_line = message.readline()

    if not curr_line:
        # connection closed before double clrf, this shouldn't happen
        print("oh no!")

    # Body building

    # Handle Content-Length header
    if "Content-Length" in result.headers:
        result.body = read_exact(message, int(result.headers["Content-Length"]))

    # Handle chunked webpages
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

    # After handling chunked webpage, handle gzip compressed message
    if "Content-Encoding" in result.headers and result.headers["Content-Encoding"] == "gzip":
        result.body = gzip.decompress(result.body)

    return result

# Builds an HTTP request with the header items and body if it is given.
# Returns an encoded byte array of the request to be sent to the web server.
def build_request(method, path, headers, body):

    if body:
        headers["Content-Length"] = str(len(body.encode()))

    result = f"{method} {path} HTTP/1.1\r\n"
    for key, value in headers.items():
        result += f"{key}: {value}\r\n"
    result += "\r\n"
    if body: result += body

    return result.encode()

def get_status_code(http_message):
    status_line = http_message.start_line.strip()
    status_words = status_line.split()
    if len(status_words) >= 2 and status_words[0].startswith("HTTP") and status_words[1].isdigit():
        return int(status_words[1])
    raise ValueError("http message is not a properly formatted response message")
    
# Builds the body of the login request message to be sent when first connecting to Fakebook.
# Used in main to login and receive the login cookie for use in the crawler.
def build_url_params(params):
    return "&".join([f"{name}={value}" for name, value in params.items()])

