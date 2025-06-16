from fastapi import HTTPException

from src.db.exceptions import DBModelNotFoundException
from src.transfer.application.interfaces.transfer_client import ITransferClient, TToken
from src.transfer.application.interfaces.unit_of_work import ITransferUnitOfWork
from src.transfer.domain.entities import SourceTokenUpdate


async def get_transfer_token(uow: ITransferUnitOfWork, transfer_client: ITransferClient, user_id: str,
                             app_bundle: str) -> TToken:
    try:
        source_token = await uow.source_tokens.get_by_user(
            user_id, app_bundle, transfer_client.SOURCE
        )
    except DBModelNotFoundException:
        raise HTTPException(400, detail="Source for user not connected")

    token = await transfer_client.parse_and_validate_token(
        source_token.token_data
    )
    # Save token each time for refresh case
    await uow.source_tokens.update_by_user(
        user_id,
        app_bundle,
        transfer_client.SOURCE,
        SourceTokenUpdate(token_data=token.model_dump_json()),
    )
    await uow.commit()

    return token
