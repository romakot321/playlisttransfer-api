from fastapi import FastAPI, Header, Request, HTTPException
from src.core.config import settings
from starlette.middleware.base import BaseHTTPMiddleware


class TokenAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, token=settings.API_TOKEN):
        super().__init__(app)
        self.token = token

    async def dispatch(self, request: Request, call_next):
        api_token = request.headers.get("Api-Token")

        if api_token != self.token:
            raise HTTPException(status_code=401, detail="Unauthorized")

        response = await call_next(request)
        return response


def validate_api_token_header(api_token: str = Header()):
    if api_token != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
