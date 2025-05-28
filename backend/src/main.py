from fastapi import FastAPI

from src.transfer.api.rest import router as transfer_router

app = FastAPI()

app.include_router(transfer_router, tags=["Transfer"], prefix="/api/transfer")
