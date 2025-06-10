from pydantic import BaseModel, Field


class SpotifyAuthData(BaseModel):
    code: str
    state: str


class SpotifyToken(BaseModel):
    access_token: str
    refresh_token: str


class SpotifyResponse(BaseModel):
    limit: int
    offset: int
    total: int
    items: list[dict]


class SpotifyPlaylist(BaseModel):
    class SpotifyPlaylistImage(BaseModel):
        url: str
        width: int | None = None
        height: int | None = None

    class SpotifyPlaylistTracksInfo(BaseModel):
        total: int

    description: str | None = None
    id: str
    images: list[SpotifyPlaylistImage] | None = Field(description="Expire in 1 day", default=None)
    name: str
    uri: str
    tracks: SpotifyPlaylistTracksInfo


class SpotifyTrack(BaseModel):
    class SpotifyTrackData(BaseModel):
        class SpotifyTrackArtist(BaseModel):
            id: str
            name: str
            uri: str

        name: str
        id: str
        uri: str
        artists: list[SpotifyTrackArtist]

    track: SpotifyTrackData


class SpotifyAlbum(BaseModel):
    class SpotifyAlbumData(BaseModel):
        class SpotifyAlbumArtist(BaseModel):
            id: str
            name: str

        total_tracks: int
        id: str
        name: str
        uri: str
        artists: list[SpotifyAlbumArtist]

    album: SpotifyAlbumData


class SpotifyUser(BaseModel):
    display_name: str
    id: str
    uri: str
