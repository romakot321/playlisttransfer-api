from typing import Annotated
from fastapi import Depends, HTTPException, Query
from src.integration.api.dependencies import get_spotify_client
from src.transfer.application.interfaces.transfer_client import ITransferClient
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.entities import TransferSource
from src.transfer.infrastructure.db.unit_of_work import PGTransferUnitOfWork


def get_transfer_client(source: TransferSource = Query()) -> ITransferClient:
    if source == TransferSource.SPOTIFY:
        return get_spotify_client()
    raise HTTPException(400, detail="Source not implemented yet")


def get_from_transfer_client(from_source: TransferSource = Query()) -> ITransferClient:
    return get_transfer_client(from_source)


def get_to_transfer_client(to_source: TransferSource = Query()) -> ITransferClient:
    return get_transfer_client(to_source)


def get_transfer_uow() -> ITransferUnitOfWork:
    return PGTransferUnitOfWork()


TransferClientDepend = Annotated[ITransferClient, Depends(get_transfer_client)]
FromTransferClientDepend = Annotated[ITransferClient, Depends(get_from_transfer_client)]
ToTransferClientDepend = Annotated[ITransferClient, Depends(get_to_transfer_client)]
TransferUoWDepend = Annotated[ITransferUnitOfWork, Depends(get_transfer_uow)]
