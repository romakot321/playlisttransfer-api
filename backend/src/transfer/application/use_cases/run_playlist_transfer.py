from uuid import UUID
from loguru import logger
import datetime as dt
from fastapi import HTTPException
from src.db.exceptions import DBModelNotFoundException
from src.transfer.application.integration_utils import get_transfer_token
from src.integration.domain.entities import Playlist, Track
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.dtos import TransferPlaylistCreateDTO
from src.transfer.domain.entities import Transfer, TransferStatus, TransferUpdate


class RunPlaylistTransferUseCase:
    def __init__(
        self, from_transfer_client: ITransferClient, to_transfer_client: ITransferClient, uow: ITransferUnitOfWork
    ) -> None:
        self.from_transfer_client = from_transfer_client
        self.to_transfer_client = to_transfer_client
        self.uow = uow
        self._from_token: TToken | None = None
        self._to_token: TToken | None = None

    async def execute(self, transfer_id: UUID, dto: TransferPlaylistCreateDTO) -> None:
        logger.info(f"Started transfer {transfer_id} {dto=}")
        async with self.uow:
            await self.set_transfer_status(transfer_id, TransferStatus.started)
            playlist = await self._transfer(transfer_id, dto)
            await self.set_transfer_status(transfer_id, TransferStatus.finished, result=playlist.model_dump_json())
        logger.info(f"Finished transfer {transfer_id}")

    async def _transfer(self, transfer_id, dto) -> Playlist:
        try:
            await self.get_from_transfer_token(dto)
            await self.get_to_transfer_token(dto)
            tracks = await self.get_tracks_to_transfer(dto)
            playlist = await self.transfer_tracks(tracks)
        except Exception as e:
            await self.set_transfer_status(transfer_id, TransferStatus.failed, error=str(e))
            raise e
        return playlist

    async def set_transfer_status(
        self, transfer_id: UUID, status: TransferStatus, error: str | None = None, result: str | None = None
    ):
        await self.uow.transfers.update_by_pk(transfer_id, TransferUpdate(status=status, error=error, result=result))
        await self.uow.commit()

    async def get_tracks_to_transfer(self, dto: TransferPlaylistCreateDTO) -> list[Track]:
        return await self.from_transfer_client.get_user_playlist_tracks(self._from_token, dto.playlist_id)

    async def search_for_tracks(self, tracks: list[Track]) -> list[str]:
        ret = []
        for track in tracks:
            founded_track_id = await self.to_transfer_client.search_for_track(
                self._to_token, track.name + " " + track.artist_name
            )
            ret.append(founded_track_id)
        return ret

    async def transfer_tracks(self, tracks: list[Track]) -> Playlist:
        new_playlist = await self.to_transfer_client.create_user_playlist(
            self._to_token, "Transfered " + dt.date.today().isoformat()
        )
        tracks_ids = await self.search_for_tracks(tracks)
        await self.to_transfer_client.add_tracks_to_playlist(self._to_token, new_playlist.source_id, *tracks_ids)
        return new_playlist

    async def get_from_transfer_token(self, dto: TransferPlaylistCreateDTO) -> None:
        self._from_token = await get_transfer_token(self.uow, self.from_transfer_client, dto.user_id, dto.app_bundle)

    async def get_to_transfer_token(self, dto: TransferPlaylistCreateDTO) -> None:
        self._to_token = await get_transfer_token(self.uow, self.to_transfer_client, dto.user_id, dto.app_bundle)
