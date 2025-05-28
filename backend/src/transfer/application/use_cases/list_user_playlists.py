from fastapi import HTTPException
from src.db.exceptions import DBModelNotFoundException
from src.integration.domain.entities import Playlist
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.dtos import UserPlaylistListDTO


class ListUserPlaylistsUseCase:
    def __init__(self, transfer_client: ITransferClient, uow: ITransferUnitOfWork) -> None:
        self.transfer_client = transfer_client
        self.uow = uow

    async def execute(self, dto: UserPlaylistListDTO) -> list[Playlist]:
        async with self.uow:
            token = await self.get_transfer_token(dto)
            playlists = await self.transfer_client.get_user_playlists(token)
        return playlists

    async def get_transfer_token(self, dto: UserPlaylistListDTO) -> TToken:
        try:
            source_token = await self.uow.source_tokens.get_by_user(dto.user_id, dto.app_bundle, self.transfer_client.SOURCE)
        except DBModelNotFoundException:
            raise HTTPException(400, detail="Source for user not connected")
        return await self.transfer_client.parse_and_validate_token(source_token.token_data)
