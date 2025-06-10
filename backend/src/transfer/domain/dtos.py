from enum import Enum
from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field

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
    from_source: TransferSource
    to_source: TransferSource
    playlist_id: str


class TransferAlbumCreateDTO(BaseModel):
    user_id: str
    app_bundle: str
    from_source: TransferSource
    to_source: TransferSource
    album_id: str


class TransferReadDTO(BaseModel):
    id: UUID
    status: TransferStatus
    error: str | None = None
    user_id: str
    app_bundle: str


class PlaylistReadDTO(BaseModel):
    id: str = Field(validation_alias=AliasChoices("source_id", "id"))
    name: str
    source: TransferSource
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

