from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from src.transfer.api.dependencies import FromTransferClientDepend, ToTransferClientDepend, TransferClientDepend, TransferUoWDepend
from src.transfer.application.use_cases.connect_source import ConnectSourceUseCase
from src.transfer.application.use_cases.create_transfer import CreateTransferUseCase
from src.transfer.application.use_cases.get_transfer import GetTransferUseCase
from src.transfer.application.use_cases.list_playlist_tracks import ListPlaylistTracksUseCase
from src.transfer.application.use_cases.list_user_albums import ListUserAlbumsUseCase
from src.transfer.application.use_cases.list_user_favorite_tracks import ListUserFavoriteTracksUseCase
from src.transfer.application.use_cases.list_user_playlists import ListUserPlaylistsUseCase
from src.transfer.application.use_cases.run_album_transfer import RunAlbumTransferUseCase
from src.transfer.application.use_cases.run_playlist_transfer import RunPlaylistTransferUseCase
from src.transfer.domain.dtos import PlaylistReadDTO, PlaylistTracksListDTO, TrackReadDTO, TransferAlbumCreateDTO, TransferPlaylistCreateDTO, TransferReadDTO, UserAlbumListDTO, UserPlaylistListDTO, UserSourceConnectDTO
from src.core.auth import validate_api_token_header

router = APIRouter(dependencies=[Depends(validate_api_token_header)])


@router.post("/source/connect", status_code=202)
async def connect_source(data: UserSourceConnectDTO, transfer_client: TransferClientDepend, uow: TransferUoWDepend):
    return await ConnectSourceUseCase(transfer_client, uow).execute(data)


@router.post("/playlist", response_model=TransferReadDTO)
async def start_playlist_transfer(data: TransferPlaylistCreateDTO, from_transfer_client: FromTransferClientDepend, to_transfer_client: ToTransferClientDepend, uow: TransferUoWDepend, background_tasks: BackgroundTasks):
    transfer = await CreateTransferUseCase(uow).execute(data)
    background_tasks.add_task(RunPlaylistTransferUseCase(from_transfer_client, to_transfer_client, uow).execute, transfer.id, data)
    return transfer


@router.post("/album", response_model=TransferReadDTO)
async def start_album_transfer(data: TransferAlbumCreateDTO, from_transfer_client: FromTransferClientDepend, to_transfer_client: ToTransferClientDepend, uow: TransferUoWDepend, background_tasks: BackgroundTasks):
    transfer = await CreateTransferUseCase(uow).execute(data)
    background_tasks.add_task(RunAlbumTransferUseCase(from_transfer_client, to_transfer_client, uow).execute, transfer.id, data)
    return transfer


@router.get("/playlist", response_model=list[PlaylistReadDTO])
async def get_user_playlists(transfer_client: TransferClientDepend, uow: TransferUoWDepend, params: UserPlaylistListDTO = Depends()):
    return await ListUserPlaylistsUseCase(transfer_client, uow).execute(params)


@router.get("/favorite", response_model=list[TrackReadDTO])
async def get_user_favorite_tracks(transfer_client: TransferClientDepend, uow: TransferUoWDepend, params: PlaylistTracksListDTO = Depends()):
    return await ListUserFavoriteTracksUseCase(transfer_client, uow).execute(params)


@router.get("/playlist/tracks", response_model=list[TrackReadDTO])
async def get_user_playlist_tracks(transfer_client: TransferClientDepend, uow: TransferUoWDepend, params: PlaylistTracksListDTO = Depends()):
    return await ListPlaylistTracksUseCase(transfer_client, uow).execute(params)


@router.get("/album/tracks", response_model=list[TrackReadDTO])
async def get_user_album_tracks(transfer_client: TransferClientDepend, uow: TransferUoWDepend, params: PlaylistTracksListDTO = Depends()):
    raise HTTPException(400, detail="Not implemented")


@router.get("/album", response_model=list[PlaylistReadDTO])
async def get_user_albums(transfer_client: TransferClientDepend, uow: TransferUoWDepend, params: UserAlbumListDTO = Depends()):
    return await ListUserAlbumsUseCase(transfer_client, uow).execute(params)


@router.get("/{transfer_id}", response_model=TransferReadDTO)
async def get_transfer(transfer_id: UUID, uow: TransferUoWDepend):
    return await GetTransferUseCase(uow).execute(transfer_id)

