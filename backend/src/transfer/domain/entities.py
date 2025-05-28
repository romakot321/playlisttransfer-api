from enum import Enum
from uuid import UUID
from pydantic import BaseModel


class TransferSource(str, Enum):
    SPOTIFY = "spotify"


class TransferStatus(str, Enum):
    queued = 'queued'
    started = 'started'
    finished = 'finished'
    failed = 'failed'


class Transfer(BaseModel):
    id: UUID
    status: TransferStatus
    error: str | None = None
    user_id: str
    app_bundle: str


class TransferCreate(BaseModel):
    user_id: str
    app_bundle: str


class TransferUpdate(BaseModel):
    status: TransferStatus | None = None
    error: str | None = None


class SourceToken(BaseModel):
    source: TransferSource
    user_id: str
    app_bundle: str
    token_data: str


class SourceTokenCreate(BaseModel):
    source: TransferSource
    user_id: str
    app_bundle: str
    token_data: str


class SourceTokenUpdate(BaseModel):
    token_data: str | None = None

