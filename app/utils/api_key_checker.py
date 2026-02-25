from fastapi import Request, HTTPException, status

ALLOWED_DOMAINS = {
    "https://researchers.aztu.edu.az",
    "http://localhost:5173",
    "http://researchers.karamshukurlu.site"
}

def check_api_key(request: Request):
    origin = request.headers.get("origin")

    if origin in ALLOWED_DOMAINS:
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
