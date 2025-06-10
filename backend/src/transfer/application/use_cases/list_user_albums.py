from fastapi import HTTPException
from src.db.exceptions import DBModelNotFoundException
from src.integration.domain.exceptions import ExternalApiUnauthorizedError
from src.transfer.application.integration_utils import get_transfer_token
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
            token = await get_transfer_token(self.uow, self.transfer_client, dto.user_id, dto.app_bundle)
            try:
                albums = await self.transfer_client.get_user_albums(token)
            except ExternalApiUnauthorizedError:
                raise HTTPException(
                    401, detail="Source tokens expired. Please, connect source again"
                ) from ExternalApiUnauthorizedError
        return albums
