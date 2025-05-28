from typing import Generic
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from fastapi import HTTPException

from src.integration.domain.entities import Album
from src.integration.domain.exceptions import ExternalApiEmptyResponseError, ExternalApiError, ExternalApiInvalidResponseError


class GetUserAlbumsUseCase(Generic[TToken]):
    def __init__(self, transfer_client: ITransferClient) -> None:
        self.transfer_client = transfer_client

    async def execute(self, token: TToken) -> list[Album]:
        try:
            return await self.transfer_client.get_user_albums(token)
        except ExternalApiEmptyResponseError as e:
            raise HTTPException(404, detail=e.detail or "Not found")
        except ExternalApiInvalidResponseError as e:
            raise HTTPException(400, detail=e.detail or "Unexpected response from source")
        except ExternalApiError as e:
            raise HTTPException(500, detail=e.detail)
