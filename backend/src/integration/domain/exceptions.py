class ExternalApiError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail


class ExternalApiEmptyResponseError(ExternalApiError):
    pass


class ExternalApiInvalidResponseError(ExternalApiError):
    pass


class ExternalApiUnauthorizedError(ExternalApiError):
    pass
