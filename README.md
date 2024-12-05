# ministarlette

PythonのASGIフレームワークである[Starlette](https://www.starlette.io/)のミニマムな再実装です🌟

サンプルコード

```python
import uvicorn
from ministarlette.application import MiniStarlette
from ministarlette.requests import Request

app = MiniStarlette()

@app.route("/echo")
async def echo(request):
    return "Hello, World!"

@app.route("/echo", methods=["POST"])
async def echo_post(request: Request):
    data = await request.json()
    return data

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
```


## Getting Started

サーバ起動

```
poetry install
poetry run python examples/main.py
```

click -> http://127.0.0.1:8000/echo


## Note
現時点(2024/12/05)では Request以外(Response, MiniStarlette本体)はシンプルな作りになっています。

今後本家の実装に寄せていきます。
