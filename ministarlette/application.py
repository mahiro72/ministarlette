from typing import Dict, Callable, List
from ministarlette.requests import Request
from ministarlette.responses import Response

class MiniStarlette:
    def __init__(self):
        self.routes: Dict[str, Dict[str, Callable]] = {} # path -> method(GET,POST,..) -> handler
        self.middleware: List[Callable] = []

    async def __call__(self, scope: Dict, receive: Callable, send: Callable):
        """
        scope: ASGIのスコープ。HTTPリクエストのメタデータが入っている
        receive: ASGIサーバからのデータを受け取るためのコールバック関数
        send: ASGIサーバにデータを送信するためのコールバック関数
    
        詳細はこちら: https://asgi.readthedocs.io/en/latest/specs/main.html#applications
        """
        if scope["type"] != "http":
            # websocketなどは未対応
            return

        request = Request(scope=scope, receive=receive)
        response = await self._handle_request(request)

        # HTTPレスポンスのメタデータ
        await send({
            "type": "http.response.start",
            "status": response.status_code,
            "headers": response.headers
        })

        # HTTPレスポンスのボディ
        await send({
            "type": "http.response.body",
            "body": response.body
        })
        # sendは2回呼び出されているが、ASGIサーバ側で内部でバッファリングし、1度のHTTPレスポンスにまとめてクライアントに返却してるぽい

    def route(self, path: str, methods: List[str] = ["GET"]):
        def decorator(func: Callable):
            for method in methods:
                if path not in self.routes:
                    self.routes[path] = {}
            self.routes[path][method] = func
            return func
        return decorator

    async def _handle_request(self, request: Request) -> Response:
        if request.path not in self.routes or request.method not in self.routes[request.path]:
            return Response(content="Not Found", status_code=404)

        handler = self.routes[request.path][request.method]
        try:
            response = await handler(request)
            return response if isinstance(response, Response) else Response(str(response))
        except Exception as e:
            return Response(str(e), 500)
