from pydantic import BaseModel, Field, AliasChoices


class YoutubeToken(BaseModel):
    token: str = Field(validation_alias=AliasChoices("token", "access_token"))
    refresh_token: str = Field(validation_alias=AliasChoices("refresh_token"))


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
        channel_title: str | None = Field(validation_alias="channelTitle", default=None)
        playlist_id: str | None = Field(validation_alias="playlistId", default=None)
        thumbnails: dict[str, YoutubeTrackSnippetThumbnail]
        resource_id: YoutubeTrackSnippetResourceId | str | None = Field(validation_alias="resourceId", default=None)

    id: str | dict
    etag: str
    snippet: YoutubeTrackSnippet
