import json
from loguru import logger
from typing import TypeVar
from pydantic import BaseModel, ValidationError
from src.integration.application.interfaces.http_client import IHTTPClient
from src.integration.domain.exceptions import (
    ExternalApiEmptyResponseError,
    ExternalApiError,
    ExternalApiInvalidResponseError,
    ExternalApiUnauthorizedError,
)
from src.integration.infrastructure.http.api_client import HTTPApiClient
from src.integration.domain.entities import Album, MusicSource, Playlist, Track
from src.integration.infrastructure.external_api.youtube_music.entities import (
    YoutubePlaylist,
    YoutubeResponse,
    YoutubeToken,
    YoutubeTrack,
)
from src.transfer.application.interfaces.transfer_client import ITransferClient
from src.core.config import settings

T = TypeVar("T", bound=BaseModel)


class YoutubeMusicTransferClient[TToken: YoutubeToken](ITransferClient):
    API_URL: str = "https://www.googleapis.com"
    API_CLIENT_ID: str = settings.YOUTUBE_CLIENT_ID
    API_CLIENT_SECRET: str = settings.YOUTUBE_CLIENT_SECRET
    SOURCE: str = MusicSource.YOUTUBE.value
    SCOPES: tuple = (
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtubepartner-channel-audit",
    )

    def __init__(self, http_client: IHTTPClient) -> None:
        self.api = HTTPApiClient(http_client, self.API_URL)

    async def _get_current_user_info(self, token: YoutubeToken) -> dict:
        response = await self.api.request(
            "GET",
            "/youtube/v3/channels",
            bearer_token=token.token,
            params={"part": "snippet", "mine": 1},
        )
        if not response.get("items"):
            raise ExternalApiEmptyResponseError()
        return response.get("items")[0]

    async def get_user_playlists(self, token: YoutubeToken) -> list[Playlist]:
        response = await self.api.request(
            "GET", "/youtube/v3/playlists", bearer_token=token.token, params={"maxResults": 50, "mine": 1, "part": "snippet,id"}
        )
        playlists = self._parse_response(response, YoutubePlaylist)
        return [self._playlist_to_domain(playlist) for playlist in playlists]

    async def get_user_playlist_tracks(self, token: YoutubeToken, playlist_id: str) -> list[Track]:
        logger.debug({"playlistId": playlist_id, "maxResults": 50, "part": "snippet"})
        response = await self.api.request(
            "GET",
            "/youtube/v3/playlistItems",
            bearer_token=token.token,
            params={"playlistId": playlist_id, "maxResults": 50, "part": "snippet"},
        )
        tracks = self._parse_response(response, YoutubeTrack)
        return [self._track_to_domain(track) for track in tracks]

    async def create_user_playlist(self, token: YoutubeToken, name: str) -> str:
        resource = {"snippet": {"title": name}}
        response = await self.api.request("POST", "/youtube/v3/playlists", bearer_token=token.token, json=resource)
        try:
            playlist = YoutubePlaylist.model_validate(response)
        except ValidationError:
            raise ExternalApiInvalidResponseError()
        return playlist.id

    async def search_for_track(self, token: YoutubeToken, query: str) -> str:
        response = await self.api.request(
            "GET",
            "/youtube/v3/search",
            bearer_token=token.token,
            params={"part": "snippet", "q": query, "type": "video", "videoCategoryId": "10", "maxResults": 1},
        )
        tracks: list[YoutubeTrack] = self._parse_response(response, YoutubeTrack)
        return (
            tracks[0].snippet.resource_id.model_dump_json()
            if not isinstance(tracks[0].snippet.resource_id, str)
            else tracks[0].snippet.resource_id
        )

    async def _refresh_token(self, token: YoutubeToken) -> YoutubeToken:
        json = {
            "client_id": self.API_CLIENT_ID,
            "client_secret": self.API_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        }
        data = "&".join(f"{k}={v}" for k, v in json.items())

        response = await self.api.client.post(
            "https://oauth2.googleapis.com/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return YoutubeToken(token=response.get("access_token"), refresh_token=token.refresh_token)

    async def parse_and_validate_token(self, token_raw: str) -> YoutubeToken:
        token = YoutubeToken.model_validate_json(token_raw)
        try:
            user = await self._get_current_user_info(token)
        except (ExternalApiEmptyResponseError, ExternalApiUnauthorizedError):
            token = await self._refresh_token(token)
        return token

    async def get_user_albums(self, token: YoutubeToken) -> list[Album]:
        raise ExternalApiError("Youtube not implemented user albums")

    async def add_user_album(self, token: YoutubeToken, album_name: str, artist_name: str) -> None:
        raise ExternalApiError("Youtube not implemented user albums")

    async def add_tracks_to_playlist(self, token: YoutubeToken, playlist_id: str, *track_ids: str) -> None:
        for track_id in track_ids:
            if track_id.startswith("{"):
                track_id = json.loads(track_id)
            resource = {"snippet": {"playlistId": playlist_id, "resourceId": track_id}}
            await self.api.request("POST", "/youtube/v3/playlistItems", bearer_token=token.token, json=resource)

    @staticmethod
    def _parse_response(response: dict, items_model: T) -> list[T]:
        try:
            result = YoutubeResponse.model_validate(response)
            if not result.items:
                raise ExternalApiEmptyResponseError()
            items = [items_model.model_validate(i) for i in result.items]
        except ValidationError as e:
            raise ExternalApiInvalidResponseError(str(e))
        return items

    @staticmethod
    def _playlist_to_domain(model: YoutubePlaylist) -> Playlist:
        return Playlist(
            source_id=model.id,
            source=MusicSource.YOUTUBE,
            name=model.snippet.title,
            image_url=model.snippet.thumbnails[list(model.snippet.thumbnails.keys())[0]].url
            if model.snippet.thumbnails
            else None,
        )

    @staticmethod
    def _track_to_domain(model: YoutubeTrack) -> Track:
        return Track(
            source_id=model.snippet.resource_id
            if isinstance(model.snippet.resource_id, str)
            else model.snippet.resource_id.model_dump_json(),
            source=MusicSource.YOUTUBE,
            name=model.snippet.title,
            artist_name=model.snippet.channel_title,
            image_url=model.snippet.thumbnails[list(model.snippet.thumbnails.keys())[0]].url
            if model.snippet.thumbnails
            else None,
        )
