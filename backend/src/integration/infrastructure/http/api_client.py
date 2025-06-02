from typing import Literal
from src.integration.application.interfaces.http_client import IHTTPClient


class HTTPApiClient:
    def __init__(
        self, client: IHTTPClient, api_url: str, bearer_token: str | None = None
    ) -> None:
        self.client = client
        self.base_url = api_url.rstrip("/")
        self.bearer_token = bearer_token

    async def request(
        self,
        method: Literal["POST", "GET", "PUT"],
        path: str,
        bearer_token: str | None = None,
        headers: dict[str, str] | None = None,
        json: dict | None = None,
        params: dict | None = None,
        data: str | None = None,
        form: dict | None = None,
    ):
        if (token := (bearer_token or self.bearer_token)):
            headers = (headers or {}) | {"Authorization": "Bearer " + token}
        url = self.base_url + "/" + path.lstrip("/")

        func = getattr(self.client, method.lower())
        return await func(
            url,
            path=path,
            headers=headers,
            json=json,
            params=params,
            data=data,
            form=form,
        )
