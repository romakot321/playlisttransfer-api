from src.transfer.application.interfaces.transfer_client import ITransferClient


class GetAuthLinkUseCase:
    def __init__(self, transfer_client: ITransferClient) -> None:
        self.transfer_client = transfer_client

    def execute(self) -> str:
        return self.transfer_client.get_oauth2_authorize_link()
