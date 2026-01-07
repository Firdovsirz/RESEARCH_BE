from fastapi import Request, HTTPException, status

ALLOWED_ORIGINS = {
    "https://researchers.aztu.edu.az",
    "http://localhost:5173"
}

async def api_key_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    api_key_header = request.headers.get("x-api-key")

    if origin in ALLOWED_ORIGINS:
        return await call_next(request)

    if api_key_header != request.app.state.check_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    return await call_next(request)