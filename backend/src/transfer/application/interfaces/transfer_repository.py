import abc
from uuid import UUID

from src.transfer.domain.entities import Transfer, TransferCreate, TransferUpdate


class ITransferRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_pk(self, pk: UUID) -> Transfer: ...

    @abc.abstractmethod
    async def create(self, transfer_data: TransferCreate) -> Transfer: ...

    @abc.abstractmethod
    async def update_by_pk(self, pk: UUID, transfer_data: TransferUpdate) -> Transfer: ...
