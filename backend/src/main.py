from fastapi import FastAPI

from src.core.logging_setup import setup_fastapi_logging
from src.transfer.api.rest import router as transfer_router

app = FastAPI()
setup_fastapi_logging(app)

app.include_router(transfer_router, tags=["Transfer"], prefix="/api/transfer")
