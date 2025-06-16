import aiohttp
from loguru import logger

from src.integration.application.interfaces.http_client import IHTTPClient
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
            if not response.ok:
                raise ExternalApiError(await response.text())
            body = await response.json()
        return body

    async def get(
            self,
            url: str,
            headers: dict[str, str] | None = None,
            params: dict[str, str | int] | None = None,
            **kwargs
    ) -> dict:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers, params=params)
            if response.status == 401:
                raise ExternalApiUnauthorizedError(detail=await response.text())
            if not response.ok:
                error_text = await response.text()
                logger.warning(error_text)
                raise ExternalApiError(detail=error_text)
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
    ) -> dict | None:
        if isinstance(form, dict):
            form = "&".join(f"{k}={v}" for k, v in form.items())
            data = (data or "") + form
        async with aiohttp.ClientSession() as session:
            response = await session.put(
                url, headers=headers, params=params, json=json, data=data
            )
            if response.status == 401:
                raise ExternalApiUnauthorizedError()
            if not response.ok:
                raise ExternalApiError(await response.text())
            try:
                body = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                body = None
        return body
