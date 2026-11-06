"""One-shot local callback server for the OAuth auth-code redirect."""
import asyncio
import threading

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
async def callback(request: Request):
    app.state.auth_code = request.query_params.get("code")
    app.state.auth_state = request.query_params.get("state")
    if hasattr(app.state, "event"):
        app.state.event.set()
    return "Authorization code received. You can close this window."


def run_server(event, host="127.0.0.1", port=8080):
    app.state.event = event
    app.state.auth_code = None
    app.state.auth_state = None
    config = uvicorn.Config(app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config)
    app.state.server = server

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def serve():
            try:
                await server.serve()
            finally:
                server.force_exit = True

        loop.run_until_complete(serve())

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return app, thread
