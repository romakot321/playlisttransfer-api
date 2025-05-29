from src.integration.infrastructure.external_api.youtube_music.transfer_client import YoutubeMusicTransferClient
from src.transfer.application.interfaces.transfer_client import ITransferClient
from src.integration.infrastructure.external_api.spotify.transfer_client import SpotifyTransferClient
from src.integration.infrastructure.http.async_client import HTTPAsyncClient
from src.core.config import settings


def get_spotify_client() -> ITransferClient:
    return SpotifyTransferClient(HTTPAsyncClient(), settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)


def get_youtube_client() -> ITransferClient:
    return YoutubeMusicTransferClient(HTTPAsyncClient())
