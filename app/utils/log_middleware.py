import os
import json
import asyncio
import logging
from fastapi import Request
from datetime import datetime
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("uvicorn.access")

class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get request info
        ip = request.client.host
        method = request.method
        path = request.url.path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            body_bytes = await request.body()
            request_body = body_bytes.decode("utf-8")
        except Exception:
            request_body = ""

        response = await call_next(request)

        try:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            response.body_iterator = iterate_in_threadpool(iter([response_body]))
            response_text = response_body.decode("utf-8")
        except Exception:
            response_text = ""

        log_data = {
            "timestamp": timestamp,
            "ip": ip,
            "method": method,
            "path": path,
            "request_body": request_body,
            "response_body": response_text,
            "status_code": response.status_code,
        }

        log_filename = datetime.now().strftime("%Y-%m-%d") + ".json"
        log_path = os.path.join(LOG_DIR, log_filename)

        async def write_log():
            async with asyncio.Lock():
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_data) + "\n")

        asyncio.create_task(write_log())

        return response

def log_requests(app):
    app.add_middleware(LogRequestsMiddleware)
