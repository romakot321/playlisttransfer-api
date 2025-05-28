from enum import Enum
from pydantic import BaseModel


class MusicSource(str, Enum):
    SPOTIFY = "spotify"


class Playlist(BaseModel):
    source_id: str
    source: MusicSource
    name: str
    tracks_count: int | None = None
    image_url: str | None = None


class Album(BaseModel):
    source_id: str
    source: MusicSource
    name: str
    artist_name: str
    tracks_count: int | None = None
    image_url: str | None = None


class Track(BaseModel):
    source_id: str
    source: MusicSource
    name: str
    artist_name: str
