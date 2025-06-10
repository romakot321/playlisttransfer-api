import base64
from loguru import logger
from pydantic import ValidationError

from src.integration.application.interfaces.http_client import IHTTPClient
from src.transfer.application.interfaces.transfer_client import (
    ITransferClient,
    TAuthData,
    TToken,
)
from src.integration.domain.entities import Album, MusicSource, Playlist, Track
from src.integration.domain.exceptions import ExternalApiEmptyResponseError, ExternalApiError, ExternalApiInvalidResponseError, ExternalApiUnauthorizedError
from src.integration.infrastructure.external_api.spotify.entities import (
    SpotifyAlbum,
    SpotifyAuthData,
    SpotifyPlaylist,
    SpotifyResponse,
    SpotifyToken,
    SpotifyTrack,
    SpotifyUser,
)


class SpotifyTransferClient[TAuthData: SpotifyAuthData, TToken: SpotifyToken](
    ITransferClient
):
    API_URL: str = "https://api.spotify.com"
    SOURCE: str = MusicSource.SPOTIFY.value
    SCOPE: str = "playlist-read-private playlist-read-public playlist-modify-private playlist-modify-public user-read-private user-library-modify user-library-read"
    STATE: str = "c459138cn57"

    def __init__(
        self, http_client: IHTTPClient[dict], client_id: str, client_secret: str
    ) -> None:
        self.http_client = http_client
        self._client_id = client_id
        self._client_secret = client_secret

    def get_oauth2_authorize_link(self) -> str:
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "scope": self.SCOPE,
            "redirect_uri": "REDIRECTURI",
            "state": self.STATE,
        }
        return "https://accounts.spotify.com/authorize?" + "&".join(
            f"{k}={v}" for k, v in params.items()
        )

    async def _get_current_user_info(self, access_token: str) -> SpotifyUser:
        response = await self.http_client.get(
            self.API_URL + "/v1/me", headers={"Authorization": "Bearer " + access_token}
        )
        try:
            return SpotifyUser.model_validate(response)
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))

    async def get_user_albums(self, token: SpotifyToken) -> list[Album]:
        response = await self.http_client.get(self.API_URL + "/v1/me/albums", params={"limit": 50}, headers={"Authorization": "Bearer " + token.access_token})
        try:
            result = SpotifyResponse.model_validate(response)
            if not result.items:
                raise ExternalApiEmptyResponseError()
            albums = [SpotifyAlbum.model_validate(i) for i in result.items]
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return [
            self._album_to_domain(album)
            for album in albums
        ]

    async def get_user_playlists(self, token: SpotifyToken) -> list[Playlist]:
        response = await self.http_client.get(
            self.API_URL + "/v1/me/playlists",
            params={"limit": 50},
            headers={"Authorization": "Bearer " + token.access_token},
        )
        try:
            result = SpotifyResponse.model_validate(response)
            if not result.items:
                raise ExternalApiEmptyResponseError()
            playlists = [SpotifyPlaylist.model_validate(i) for i in result.items]
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return [self._playlist_to_domain(playlist) for playlist in playlists]

    async def get_user_playlist_tracks(
        self, token: SpotifyToken, playlist_id: str
    ) -> list[Track]:
        response = await self.http_client.get(
            self.API_URL + f"/v1/playlists/{playlist_id}/tracks",
            params={"limit": 50},
            headers={"Authorization": "Bearer " + token.access_token},
        )
        try:
            result = SpotifyResponse.model_validate(response)
            if not result.items:
                raise ExternalApiEmptyResponseError()
            tracks = [SpotifyTrack.model_validate(i) for i in result.items]
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return [self._track_to_domain(track) for track in tracks]

    async def create_user_playlist(self, token: SpotifyToken, name: str) -> str:
        user_info = await self._get_current_user_info(token.access_token)
        response = await self.http_client.post(
            self.API_URL + f"/v1/users/{user_info.id}/playlists",
            headers=self._make_client_auth_header(token),
            json={"name": name},
        )
        try:
            result = SpotifyPlaylist.model_validate(response)
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return result.id

    async def add_user_album(
        self, token: SpotifyToken, album_name: str, artist_name: str
    ) -> None:
        album_id = await self.search_for_album(token, album_name, artist_name)
        await self.http_client.put(
            self.API_URL + "/v1/me/albums",
            headers={"Authorization": "Bearer " + token.access_token, "Content-Type": "application/json"},
            json={"ids": [album_id]},
        )

    async def add_tracks_to_playlist(
        self, token: SpotifyToken, playlist_id: str, *tracks_ids: list[str]
    ) -> None:
        await self.http_client.post(
            self.API_URL + f"/v1/playlists/{playlist_id}/tracks",
            json={"uris": tracks_ids},
            headers={"Authorization": "Bearer " + token.access_token},
        )

    async def search_for_track(self, token: SpotifyToken, query: str) -> str:
        response = await self.http_client.get(
            self.API_URL + "/v1/search",
            headers={"Authorization": "Bearer " + token.access_token},
            params={"q": query, "type": "track", "limit": 1},
        )
        try:
            result = SpotifyResponse.model_validate(response.get("tracks"))
            if not result.items:
                raise ExternalApiEmptyResponseError()
            track = SpotifyTrack.model_validate({"track": result.items[0]})
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return track.track.uri

    async def search_for_album(
        self, token: SpotifyToken, name: str, artist: str
    ) -> str:
        response = await self.http_client.get(
            self.API_URL + "/v1/search",
            headers={"Authorization": "Bearer " + token.access_token},
            params={"q": artist + " " + name, "type": "album", "limit": 1},
        )
        try:
            result = SpotifyResponse.model_validate(response.get("albums"))
            if not result.items:
                raise ExternalApiEmptyResponseError()
            album = SpotifyAlbum.model_validate({"album": result.items[0]})
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return album.album.id

    async def _refresh_token(self, token: SpotifyToken) -> SpotifyToken:
        response = await self.http_client.post(
            "https://accounts.spotify.com/api/token",
            form={"grant_type": "refresh_token", "refresh_token": token.refresh_token, "client_id": self._client_id},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            result = SpotifyToken.model_validate(response)
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return result

    async def parse_and_validate_token(self, token_raw: str) -> SpotifyToken:
        try:
            token = SpotifyToken.model_validate_json(token_raw)
        except ValidationError:
            raise ValueError("Invalid token")
        
        try:
            await self._get_current_user_info(token.access_token)
        except ExternalApiUnauthorizedError as e:
            token = await self._refresh_token(token)
            logger.debug(f"Refreshed token: {token}")

        return token

    def _make_server_auth_header_token(self) -> str:
        return (
            "Basic "
            + base64.b64encode(
                (self._client_id + ":" + self._client_secret).encode()
            ).decode()
        )

    def _make_client_auth_header(self, token: SpotifyToken) -> dict[str, str]:
        return {"Authorization": "Bearer " + token.access_token}

    @staticmethod
    def _playlist_to_domain(model: SpotifyPlaylist) -> Playlist:
        return Playlist(
            source_id=model.id,
            source=MusicSource.SPOTIFY,
            name=model.name,
            tracks_count=model.tracks.total,
            image_url=model.images[-1].url if model.images else None,
        )

    @staticmethod
    def _track_to_domain(model: SpotifyTrack) -> Track:
        return Track(
            source_id=model.track.id,
            source=MusicSource.SPOTIFY,
            name=model.track.name,
            artist_name=" ".join(i.name for i in model.track.artists),
        )

    @staticmethod
    def _album_to_domain(model: SpotifyAlbum) -> Album:
        return Album(
            source_id=model.album.id,
            source=MusicSource.SPOTIFY,
            name=model.album.name,
            artist_name=" ".join(i.name for i in model.album.artists)
        )
