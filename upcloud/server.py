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
    
    def run():
        import asyncio
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="error")
        server = uvicorn.Server(config)
        app.state.server = server
        
        async def serve():
            try:
                await server.serve()
            except Exception:
                pass
            finally:
                server.force_exit = True
                
        new_loop.run_until_complete(serve())
        
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
    return app, thread