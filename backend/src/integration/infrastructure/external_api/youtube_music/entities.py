from pydantic import BaseModel, Field


class YoutubeToken(BaseModel):
    token: str
    refresh_token: str


class YoutubeResponse(BaseModel):
    items: list


class YoutubePlaylist(BaseModel):
    class YoutubePlaylistSnippet(BaseModel):
        class YoutubePlaylistSnippetThumbnail(BaseModel):
            url: str
            width: int
            height: int

        title: str
        thumbnails: dict[str, YoutubePlaylistSnippetThumbnail]
        channel_title: str = Field(validation_alias="channelTitle")

    id: str
    etag: str
    snippet: YoutubePlaylistSnippet


class YoutubeTrack(BaseModel):
    class YoutubeTrackSnippet(BaseModel):
        class YoutubeTrackSnippetThumbnail(BaseModel):
            url: str
            width: int
            height: int

        class YoutubeTrackSnippetResourceId(BaseModel):
            kind: str
            video_id: str | None = Field(validation_alias="videoId", default=None)

        title: str
        channel_title: str = Field(validation_alias="channelTitle")
        playlist_id: str = Field(validation_alias="playlistId")
        thumbnails: dict[str, YoutubeTrackSnippetThumbnail]
        resource_id: YoutubeTrackSnippetResourceId | str = Field(validation_alias="resourceId")

    id: str
    etag: str
    snippet: YoutubeTrackSnippet
