import json
from typing import Generic

from src.transfer.application.interfaces.transfer_client import (
    ITransferClient,
    TAuthData,
)
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.dtos import UserSourceConnectDTO
from src.transfer.domain.entities import SourceTokenCreate, TransferSource


class ConnectSourceUseCase(Generic[TAuthData]):
    def __init__(
            self, transfer_client: ITransferClient, uow: ITransferUnitOfWork
    ) -> None:
        self.transfer_client = transfer_client
        self.uow = uow

    async def execute(self, dto: UserSourceConnectDTO) -> None:
        command = SourceTokenCreate(
            source=TransferSource(self.transfer_client.SOURCE),
            user_id=dto.user_id,
            app_bundle=dto.app_bundle,
            token_data=json.dumps(
                {"access_token": dto.access_token, "refresh_token": dto.refresh_token}
            ),
        )
        async with self.uow:
            await self.uow.source_tokens.create(command)
            await self.uow.commit()
