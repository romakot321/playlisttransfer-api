from uuid import UUID

from fastapi import HTTPException
from src.db.exceptions import DBModelNotFoundException
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.entities import Transfer


class GetTransferUseCase:
    def __init__(self, uow: ITransferUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, transfer_id: UUID) -> Transfer:
        async with self.uow:
            try:
                transfer = await self.uow.transfers.get_by_pk(transfer_id)
            except DBModelNotFoundException:
                raise HTTPException(404)
        return transfer
