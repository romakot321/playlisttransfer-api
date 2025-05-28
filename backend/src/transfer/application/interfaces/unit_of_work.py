import abc

from src.transfer.application.interfaces.source_token_repository import ISourceTokenRepository
from src.transfer.application.interfaces.transfer_repository import ITransferRepository


class ITransferUnitOfWork(abc.ABC):
    transfers: ITransferRepository
    source_tokens: ISourceTokenRepository

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def _rollback(self):
        pass

    @abc.abstractmethod
    async def _commit(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self._rollback()
