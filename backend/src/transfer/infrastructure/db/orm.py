from sqlalchemy.orm import Mapped

from src.db.base import Base, BaseMixin


class TransferDB(BaseMixin, Base):
    __tablename__ = "transfers"

    from_source: Mapped[str]
    to_source: Mapped[str]
    status: Mapped[str]
    result: Mapped[str | None]
    user_id: Mapped[str]
    app_bundle: Mapped[str]
    error: Mapped[str | None]


class SourceTokenDB(BaseMixin, Base):
    __tablename__ = "source_tokens"

    user_id: Mapped[str]
    app_bundle: Mapped[str]
    source: Mapped[str]
    token_data: Mapped[str]
