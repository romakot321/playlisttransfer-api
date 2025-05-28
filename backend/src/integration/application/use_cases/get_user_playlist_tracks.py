from typing import Generic

from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.integration.domain.entities import Track
from fastapi import HTTPException

from src.integration.domain.exceptions import ExternalApiEmptyResponseError, ExternalApiError, ExternalApiInvalidResponseError


class GetUserPlaylistTracks(Generic[TToken]):
    def __init__(self, transfer_client: ITransferClient) -> None:
        self.transfer_client = transfer_client

    async def execute(self, token: TToken, playlist_id: str) -> list[Track]:
        try:
            return await self.transfer_client.get_user_playlist_tracks(token, playlist_id)
        except ExternalApiEmptyResponseError as e:
            raise HTTPException(404, detail=e.detail or "Not found")
        except ExternalApiInvalidResponseError as e:
            raise HTTPException(400, detail=e.detail or "Unexpected response from source")
        except ExternalApiError as e:
            raise HTTPException(500, detail=e.detail)
