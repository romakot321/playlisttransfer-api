from typing import Generic

from fastapi import HTTPException

from src.integration.domain.exceptions import ExternalApiEmptyResponseError, ExternalApiError, \
    ExternalApiInvalidResponseError
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken


class SearchForTrackUseCase(Generic[TToken]):
    def __init__(self, transfer_client: ITransferClient) -> None:
        self.transfer_client = transfer_client

    async def execute(self, token: TToken, query: str) -> str:
        """Search track by query and return it's id"""
        try:
            return await self.transfer_client.search_for_track(token, query)
        except ExternalApiEmptyResponseError as e:
            raise HTTPException(404, detail=e.detail or "Not found")
        except ExternalApiInvalidResponseError as e:
            raise HTTPException(400, detail=e.detail or "Unexpected response from source")
        except ExternalApiError as e:
            raise HTTPException(500, detail=e.detail)
