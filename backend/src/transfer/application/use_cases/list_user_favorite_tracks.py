from fastapi import HTTPException
from loguru import logger

from src.db.exceptions import DBModelNotFoundException
from src.transfer.domain.dtos import TrackReadDTO, PlaylistTracksListDTO
from src.integration.domain.entities import Track
from src.integration.domain.exceptions import ExternalApiError
from src.transfer.application.integration_utils import get_transfer_token
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.application.interfaces.transfer_client import TToken, ITransferClient


class ListUserFavoriteTracksUseCase:
    def __init__(self, transfer_client: ITransferClient, uow: ITransferUnitOfWork) -> None:
        self.transfer_client = transfer_client
        self.uow = uow

    async def execute(self, dto: PlaylistTracksListDTO) -> list[TrackReadDTO]:
        async with self.uow:
            token = await get_transfer_token(self.uow, self.transfer_client, dto.user_id, dto.app_bundle)
            try:
                tracks = await self.transfer_client.get_user_favorites_tracks(token)
            except ExternalApiError as e:
                # Probably Not implemented error
                logger.exception(e)
                raise HTTPException(400, detail=e.detail) from e
        return [self._to_dto(m) for m in tracks]

    @staticmethod
    def _to_dto(model: Track) -> TrackReadDTO:
        return TrackReadDTO(
            id=model.source_id,
            name=model.name,
            artist=model.artist_name,
            image_url=model.image_url
        )
