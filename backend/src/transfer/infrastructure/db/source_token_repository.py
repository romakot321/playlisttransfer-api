from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.exceptions import DBModelConflictException, DBModelNotFoundException
from src.transfer.application.interfaces.source_token_repository import ISourceTokenRepository
from src.transfer.domain.entities import SourceToken, SourceTokenCreate, SourceTokenUpdate, TransferSource
from src.transfer.infrastructure.db.orm import SourceTokenDB


class PGSourceTokenRepository(ISourceTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def get_by_user(self, user_id: str, app_bundle: str, source: str) -> SourceToken:
        query = select(SourceTokenDB).filter_by(user_id=user_id, app_bundle=app_bundle, source=source)
        model = await self.session.scalar(query)
        if model is None:
            raise DBModelNotFoundException()
        return self._to_domain(model)

    async def create(self, data: SourceTokenCreate) -> SourceToken:
        model = SourceTokenDB(**data.model_dump(mode="json"))
        self.session.add(model)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Model can't be created. " + str(e.orig).split('\nDETAIL:  ')[1]
            except IndexError:
                detail = "Model can't be created due to integrity error."
            raise DBModelConflictException(detail)

        return self._to_domain(model)

    async def update_by_user(self, user_id: str, app_bundle: str, source: str, data: SourceTokenUpdate) -> SourceToken:
        query = update(SourceTokenDB).filter_by(user_id=user_id, app_bundle=app_bundle, source=source).values(**data.model_dump(mode="json", exclude_unset=True))
        await self.session.execute(query)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Model can't be updated. " + str(e.orig).split('\nDETAIL:  ')[1]
            except IndexError:
                detail = "Model can't be updated due to integrity error."
            raise DBModelConflictException(detail)

        return await self.get_by_user(user_id, app_bundle, source)

    @staticmethod
    def _to_domain(model: SourceTokenDB) -> SourceToken:
        return SourceToken(
            source=TransferSource(model.source),
            user_id=model.user_id,
            app_bundle=model.app_bundle,
            token_data=model.token_data
        )
