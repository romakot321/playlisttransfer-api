from fastapi import HTTPException
from src.db.exceptions import DBModelNotFoundException
from src.integration.domain.entities import Album
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.dtos import UserAlbumListDTO


class ListUserAlbumsUseCase:
    def __init__(self, transfer_client: ITransferClient, uow: ITransferUnitOfWork) -> None:
        self.transfer_client = transfer_client
        self.uow = uow

    async def execute(self, dto: UserAlbumListDTO) -> list[Album]:
        async with self.uow:
            token = await self.get_transfer_token(dto)
            albums = await self.transfer_client.get_user_albums(token)
        return albums

    async def get_transfer_token(self, dto: UserAlbumListDTO) -> TToken:
        try:
            source_token = await self.uow.source_tokens.get_by_user(dto.user_id, dto.app_bundle, self.transfer_client.SOURCE)
        except DBModelNotFoundException:
            raise HTTPException(400, detail="Source for user not connected")
        return await self.transfer_client.parse_and_validate_token(source_token.token_data)
