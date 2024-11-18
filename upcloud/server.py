import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import uvicorn
import threading
import signal

load_dotenv()

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
async def callback(request: Request):
    app.state.auth_code = request.query_params.get('code')
    if hasattr(app.state, 'event'):
        app.state.event.set()
    return "Authorization code received. You can close this window."

def run_server(event):
    app.state.event = event
    app.state.auth_code = None
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="error")
    server = uvicorn.Server(config)
    server._serve = server.run
    thread = threading.Thread(target=server._serve)
    thread.daemon = True
    thread.start()
    app.state.server = server  # Store server instance in app.state
    return app, thread