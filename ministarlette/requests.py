from typing import Dict, Callable, NoReturn, AsyncGenerator, Any, List
import json
from urllib.parse import parse_qs

class ClientDisconnect(Exception):
    pass

async def empty_receive() -> NoReturn:
    raise RuntimeError("Receive channel is empty")

class Request:
    def __init__(self, scope: Dict, receive: Callable = empty_receive):
        assert scope["type"] == "http"
        self.scope = scope
        self.query_params = parse_qs(scope['query_string'].decode())
        self.path = scope['path']
        self.method = scope['method']
        self._receive = receive # ASGIサーバからデータを受け取るためのコールバック関数
        self._stream_consumed = False #ストリームが読み取られたかどうかのフラグ

    @property
    def receive(self) -> Callable:
        return self._receive

    async def stream(self) -> AsyncGenerator[bytes, None]:
        if hasattr(self, "_body"):  # キャッシュされたbodyがあればそれを読み取る。.body()が複数回呼ばれた場合に活用される
            yield self._body
            yield b"" # 空のバイト列を返しストリームの終了を示す
            return

        if self._stream_consumed:
            raise RuntimeError("Stream consumed")
        
        while not self._stream_consumed:
            message: Dict = await self.receive() # chunk単位でデータの受け取り
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if not message.get("more_body", False): # 最後のchunkかどうか
                    self._stream_consumed = True
                if body:
                    yield body

            elif message["type"] == "http.disconnect":
                self._stream_consumed = True
                raise ClientDisconnect()
        yield b""

    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            chunks: List[bytes] = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = b"".join(chunks)
        return self._body
    
    async def json(self) -> Any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        return self._json

    # NOTE: formは実装してない
