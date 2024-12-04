import uvicorn
from ministarlette.application import MiniStarlette
from ministarlette.requests import Request

app = MiniStarlette()

# 動作確認: curl http://localhost:8000/echo
@app.route("/echo")
async def echo(request):
    return "Hello, World!"

# 動作確認: curl -X POST -d '{"name": "Alice"}' http://localhost:8000/echo
@app.route("/echo", methods=["POST"])
async def echo_post(request: Request):
    data = await request.json()
    print(f'data: {data}')
    return data

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
