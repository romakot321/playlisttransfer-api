from typing import Generic
from src.transfer.application.interfaces.transfer_client import ITransferClient, TAuthData, TToken
from fastapi import HTTPException

from src.integration.domain.exceptions import ExternalApiEmptyResponseError, ExternalApiError, ExternalApiInvalidResponseError


class AuthUserUseCase(Generic[TAuthData, TToken]):
    def __init__(self, transfer_client: ITransferClient[TAuthData, TToken]) -> None:
        self.transfer_client = transfer_client

    async def execute(self, auth_data: TAuthData) -> TToken:
        try:
            return await self.transfer_client.authorize_user(auth_data)
        except ExternalApiEmptyResponseError as e:
            raise HTTPException(404, detail=e.detail or "Not found")
        except ExternalApiInvalidResponseError as e:
            raise HTTPException(400, detail=e.detail or "Unexpected response from source")
        except ExternalApiError as e:
            raise HTTPException(500, detail=e.detail)
