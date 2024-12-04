class Response:
    def __init__(self, content: str, status_code: int = 200):
        self.body = content.encode()
        self.status_code = status_code
        self.headers = [
            (b"Content-Type", b"text/plain"),
            (b"Content-Length", str(len(content)).encode())
        ]
