from typing import Generic
from fastapi import HTTPException
from loguru import logger

from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.integration.domain.entities import Playlist
from src.integration.domain.exceptions import ExternalApiEmptyResponseError, ExternalApiError, ExternalApiInvalidResponseError


class GetUserPlaylists(Generic[TToken]):
    def __init__(self, transfer_client: ITransferClient) -> None:
        self.transfer_client = transfer_client

    async def execute(self, token: TToken) -> list[Playlist]:
        try:
            return await self.transfer_client.get_user_playlists(token)
        except ExternalApiEmptyResponseError as e:
            raise HTTPException(404, detail=e.detail or "Not found")
        except ExternalApiInvalidResponseError as e:
            raise HTTPException(400, detail=e.detail or "Unexpected response from source")
        except ExternalApiError as e:
            raise HTTPException(500, detail=e.detail)
