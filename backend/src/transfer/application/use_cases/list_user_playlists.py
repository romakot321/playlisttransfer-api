from fastapi import HTTPException
from src.db.exceptions import DBModelNotFoundException
from src.transfer.application.integration_utils import get_transfer_token
from src.transfer.domain.entities import SourceTokenUpdate
from src.integration.domain.entities import Playlist
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.dtos import UserPlaylistListDTO


class ListUserPlaylistsUseCase:
    def __init__(
        self, transfer_client: ITransferClient, uow: ITransferUnitOfWork
    ) -> None:
        self.transfer_client = transfer_client
        self.uow = uow

    async def execute(self, dto: UserPlaylistListDTO) -> list[Playlist]:
        async with self.uow:
            token = await get_transfer_token(self.uow, self.transfer_client, dto.user_id, dto.app_bundle)
            playlists = await self.transfer_client.get_user_playlists(token)
        return playlists
