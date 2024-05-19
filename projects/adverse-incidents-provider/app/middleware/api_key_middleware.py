from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader

from app.config.settings import Config

API_KEY_HEADER = "X-API-Key"


async def api_key_middleware(request: Request, api_key_header: APIKeyHeader = APIKeyHeader(name=API_KEY_HEADER)):
    api_key = await api_key_header(request)
    if not api_key or api_key != Config.INCIDENTS_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return request
