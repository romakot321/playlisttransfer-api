import abc
from typing import Generic, TypeVar

from src.integration.domain.entities import Album, Playlist, Track

TAuthData = TypeVar("TAuthData")
TToken = TypeVar("TToken")


class ITransferClient(abc.ABC, Generic[TAuthData, TToken]):
    API_URL: str
    SOURCE: str

    @abc.abstractmethod
    async def get_user_playlists(self, token: TToken) -> list[Playlist]: ...

    @abc.abstractmethod
    async def get_user_albums(self, token: TToken) -> list[Album]: ...

    @abc.abstractmethod
    async def get_user_playlist_tracks(self, token: TToken, playlist_id: str) -> list[Track]: ...

    @abc.abstractmethod
    async def get_user_favorites_tracks(self, token: TToken, total=None, offset=0, count=50) -> list[Track]:
        """Recursively gets user liked tracks"""

    @abc.abstractmethod
    async def create_user_playlist(self, token: TToken, name: str) -> Playlist: ...

    @abc.abstractmethod
    async def add_user_album(self, token: TToken, album_name: str, artist_name: str) -> None: ...

    @abc.abstractmethod
    async def add_tracks_to_playlist(self, token: TToken, playlist_id: str, *track_ids: str) -> None: ...

    @abc.abstractmethod
    async def search_for_track(self, token: TToken, track: str, artist: str) -> str:

    @abc.abstractmethod
    async def parse_and_validate_token(self, token_raw: str) -> TToken: ...
