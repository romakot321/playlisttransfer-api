from fastapi import FastAPI

from backend.src.core.auth import TokenAuthMiddleware
from src.transfer.api.rest import router as transfer_router

app = FastAPI()

app.include_router(transfer_router, tags=["Transfer"], prefix="/api/transfer")

app.add_middleware(TokenAuthMiddleware)
