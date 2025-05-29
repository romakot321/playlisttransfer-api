import abc
from typing import Generic, TypeVar

TResponse = TypeVar("TResponse")


class IHTTPClient(abc.ABC, Generic[TResponse]):
    @abc.abstractmethod
    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
        **kwargs
    ) -> TResponse: ...

    @abc.abstractmethod
    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
        json: dict | None = None,
        data: str | None = None,
        form: dict[str, str | int] | str | None = None
    ) -> TResponse: ...

    @abc.abstractmethod
    async def put(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str | int] | None = None,
        json: dict | None = None,
        data: str | None = None,
        form: dict[str, str | int] | str | None = None
    ) -> TResponse: ...
