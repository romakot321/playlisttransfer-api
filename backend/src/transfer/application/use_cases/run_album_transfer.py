from uuid import UUID

from loguru import logger

from src.integration.domain.entities import Album
from src.transfer.application.integration_utils import get_transfer_token
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.dtos import TransferAlbumCreateDTO
from src.transfer.domain.entities import TransferStatus, TransferUpdate


class RunAlbumTransferUseCase:
    def __init__(self, from_transfer_client: ITransferClient, to_transfer_client: ITransferClient,
                 uow: ITransferUnitOfWork) -> None:
        self.from_transfer_client = from_transfer_client
        self.to_transfer_client = to_transfer_client
        self.uow = uow
        self._from_token: TToken | None = None
        self._to_token: TToken | None = None

    async def execute(self, transfer_id: UUID, dto: TransferAlbumCreateDTO) -> None:
        logger.info(f"Started transfer {transfer_id} {dto=}")
        async with self.uow:
            await self.set_transfer_status(transfer_id, TransferStatus.started)
            await self._transfer(transfer_id, dto)
            await self.set_transfer_status(transfer_id, TransferStatus.finished)
        logger.info(f"Finished transfer {transfer_id}")

    async def _transfer(self, transfer_id, dto):
        try:
            await self.get_from_transfer_token(dto)
            await self.get_to_transfer_token(dto)
            album = await self.get_album_to_transfer(dto)
            await self.transfer_album(album)
        except Exception as e:
            await self.set_transfer_status(transfer_id, TransferStatus.failed, error=str(e))
            raise e

    async def set_transfer_status(self, transfer_id: UUID, status: TransferStatus, error: str | None = None):
        await self.uow.transfers.update_by_pk(transfer_id, TransferUpdate(status=status, error=error))
        await self.uow.commit()

    async def get_album_to_transfer(self, dto: TransferAlbumCreateDTO) -> Album:
        albums = await self.from_transfer_client.get_user_albums(self._from_token)
        logger.debug(albums)
        return [i for i in albums if i.source_id == dto.album_id][0]
        return next(
            filter(lambda i: i.source_id == dto.album_id, albums)
        )

    async def transfer_album(self, album: Album):
        await self.to_transfer_client.add_user_album(self._to_token, album.name, album.artist_name)

    async def get_from_transfer_token(self, dto: TransferAlbumCreateDTO) -> None:
        self._from_token = await get_transfer_token(self.uow, self.from_transfer_client, dto.user_id, dto.app_bundle)

    async def get_to_transfer_token(self, dto: TransferAlbumCreateDTO) -> None:
        self._to_token = await get_transfer_token(self.uow, self.to_transfer_client, dto.user_id, dto.app_bundle)
