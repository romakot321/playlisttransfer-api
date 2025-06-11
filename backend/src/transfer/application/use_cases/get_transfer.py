from uuid import UUID

from fastapi import HTTPException

from src.db.exceptions import DBModelNotFoundException
from src.transfer.domain.dtos import TransferReadDTO
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork


class GetTransferUseCase:
    def __init__(self, uow: ITransferUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, transfer_id: UUID) -> TransferReadDTO:
        async with self.uow:
            try:
                transfer = await self.uow.transfers.get_by_pk(transfer_id)
            except DBModelNotFoundException as e:
                raise HTTPException(404) from e
        return TransferReadDTO.model_validate(transfer.model_dump())
