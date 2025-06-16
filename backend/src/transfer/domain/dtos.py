from typing import Any
from uuid import UUID

from pydantic import Field, BaseModel, AliasChoices, field_validator

from src.transfer.domain.entities import TransferSource, TransferStatus


class UserSourceConnectDTO(BaseModel):
    user_id: str
    app_bundle: str
    access_token: str
    refresh_token: str


class PlaylistTracksListDTO(BaseModel):
    user_id: str
    app_bundle: str
    playlist_id: str


class UserPlaylistListDTO(BaseModel):
    user_id: str
    app_bundle: str


class UserAlbumListDTO(BaseModel):
    user_id: str
    app_bundle: str


class TransferPlaylistCreateDTO(BaseModel):
    user_id: str
    app_bundle: str
    playlist_id: str


class TransferAlbumCreateDTO(BaseModel):
    user_id: str
    app_bundle: str
    album_id: str


class TransferFavoriteCreateDTO(BaseModel):
    user_id: str
    app_bundle: str


class PlaylistReadDTO(BaseModel):
    id: str = Field(validation_alias=AliasChoices("source_id", "id"))
    name: str
    source: TransferSource
    url: str | None = None
    image_url: str | None = None


class AlbumReadDTO(BaseModel):
    id: str = Field(validation_alias=AliasChoices("source_id", "id"))
    name: str
    source: TransferSource
    image_url: str | None = None


class TrackReadDTO(BaseModel):
    id: str = Field(validation_alias=AliasChoices("source_id", "id"))
    name: str
    artist: str
    image_url: str | None = None


class TransferReadDTO(BaseModel):
    id: UUID
    status: TransferStatus
    error: str | None = None
    result: PlaylistReadDTO | None = None
    user_id: str
    app_bundle: str

    @field_validator("result", mode="before")
    @classmethod
    def parse_json_result(cls, value: Any, _info) -> PlaylistReadDTO:
        if not isinstance(value, str):
            return value
        return PlaylistReadDTO.model_validate_json(value)
