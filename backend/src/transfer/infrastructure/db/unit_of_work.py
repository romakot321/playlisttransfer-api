from sqlalchemy.ext.asyncio import AsyncSession
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork

from src.db.engine import async_session_maker
from src.transfer.infrastructure.db.source_token_repository import PGSourceTokenRepository
from src.transfer.infrastructure.db.transfer_repository import PGTransferRepository


class PGTransferUnitOfWork(ITransferUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.transfers = PGTransferRepository(self.session)
        self.source_tokens = PGSourceTokenRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def _rollback(self):
        await self.session.rollback()
