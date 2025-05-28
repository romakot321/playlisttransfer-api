import aiohttp

from src.integration.application.interfaces.http_client import IHTTPClient, TResponse
from src.integration.domain.exceptions import ExternalApiError, ExternalApiUnauthorizedError


class HTTPAsyncClient[TResponse: dict](IHTTPClient):
    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
        json: dict | None = None,
        data: str | None = None,
        form: dict[str, str | int] | str | None = None,
    ) -> dict:
        if isinstance(form, dict):
            form = "&".join(f"{k}={v}" for k, v in form.items())
            data = (data or "") + form
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url, headers=headers, params=params, json=json, data=data
            )
            if response.status == 401:
                raise ExternalApiUnauthorizedError()
            if response.status != 200:
                raise ExternalApiError(await response.text())
            body = await response.json()
        return body

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
    ) -> dict:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers, params=params)
            if response.status == 401:
                raise ExternalApiUnauthorizedError()
            if response.status != 200:
                raise ExternalApiError(await response.text())
            body = await response.json()
        return body

    async def put(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
        json: dict | None = None,
        data: str | None = None,
        form: dict[str, str | int] | str | None = None
    ) -> dict:
        if isinstance(form, dict):
            form = "&".join(f"{k}={v}" for k, v in form.items())
            data = (data or "") + form
        async with aiohttp.ClientSession() as session:
            response = await session.put(
                url, headers=headers, params=params, json=json, data=data
            )
            if response.status == 401:
                raise ExternalApiUnauthorizedError()
            if response.status != 200:
                raise ExternalApiError(await response.text())
            body = await response.json()
        return body
