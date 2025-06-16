from uuid import UUID

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.exceptions import DBModelConflictException, DBModelNotFoundException
from src.transfer.application.interfaces.transfer_repository import ITransferRepository
from src.transfer.domain.entities import Transfer, TransferCreate, TransferStatus, TransferUpdate
from src.transfer.infrastructure.db.orm import TransferDB


class PGTransferRepository(ITransferRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def get_by_pk(self, pk: UUID) -> Transfer:
        model = await self.session.get(TransferDB, ident=pk)
        if model is None:
            raise DBModelNotFoundException()
        return self._to_domain(model)

    async def create(self, transfer_data: TransferCreate) -> Transfer:
        model = TransferDB(**transfer_data.model_dump(mode="json"))
        self.session.add(model)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Transfer can't be created. " + str(e.orig)
            except IndexError:
                detail = "Transfer can't be created due to integrity error."
            raise DBModelConflictException(detail)

        return self._to_domain(model)

    async def update_by_pk(self, pk: UUID, transfer_data: TransferUpdate) -> Transfer:
        query = update(TransferDB).filter_by(id=pk).values(**transfer_data.model_dump(mode="json", exclude_unset=True))
        await self.session.execute(query)
        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Transfer can't be updated. " + str(e.orig).split('\nDETAIL:  ')[1]
            except IndexError:
                detail = "Transfer can't be updated due to integrity error."
            raise DBModelConflictException(detail)
        return await self.get_by_pk(pk)

    @staticmethod
    def _to_domain(model: TransferDB) -> Transfer:
        return Transfer(
            id=model.id,
            status=TransferStatus(model.status),
            error=model.error,
            user_id=model.user_id,
            app_bundle=model.app_bundle
        )
