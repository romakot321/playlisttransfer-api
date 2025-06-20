from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.dtos import TransferAlbumCreateDTO, TransferPlaylistCreateDTO, TransferFavoriteCreateDTO
from src.transfer.domain.entities import Transfer, TransferCreate


class CreateTransferUseCase:
    def __init__(self, uow: ITransferUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, from_source: str, to_source: str, dto: TransferPlaylistCreateDTO | TransferAlbumCreateDTO | TransferFavoriteCreateDTO) -> Transfer:
        command = TransferCreate(**dto.model_dump(), from_source=from_source, to_source=to_source)
        async with self.uow:
            model = await self.uow.transfers.create(command)
            await self.uow.commit()
        return model
