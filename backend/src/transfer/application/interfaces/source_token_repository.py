import abc

from src.transfer.domain.entities import SourceToken, SourceTokenCreate, SourceTokenUpdate


class ISourceTokenRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_user(self, user_id: str, app_bundle: str, source: str) -> SourceToken: ...

    @abc.abstractmethod
    async def create(self, data: SourceTokenCreate) -> SourceToken: ...

    @abc.abstractmethod
    async def update_by_user(self, user_id: str, app_bundle: str, source: str, data: SourceTokenUpdate) -> SourceToken: ...
