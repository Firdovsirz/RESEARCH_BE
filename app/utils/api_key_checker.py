import os
from fastapi import Request, HTTPException, status

def check_api_key(request: Request):
    allowed_domains_str = os.getenv("ALLOWED_DOMAINS", "")
    allowed_domains = {d.strip() for d in allowed_domains_str.split(",") if d.strip()}
    
    origin = request.headers.get("origin")

    # Only bypass API key if origin is explicitly allowed AND it's a browser request (has origin)
    if origin and origin in allowed_domains:
        return True
    
    server_api_key = getattr(request.app.state, "check_api_key", None)
    if not server_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not configured"
        )

    client_key = request.headers.get("x-api-key")
    if client_key != server_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return True
