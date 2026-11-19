from http_client import HttpClient


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




