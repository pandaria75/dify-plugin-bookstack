from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests


class BookStackError(RuntimeError):
    """Base error for BookStack API failures."""


class InvalidCredentialsError(BookStackError):
    pass


class PermissionDeniedError(BookStackError):
    pass


class BookNotFoundError(BookStackError):
    pass


class ChapterNotFoundError(BookStackError):
    pass


class PageNotFoundError(BookStackError):
    pass


class ServiceUnavailableError(BookStackError):
    pass


class InvalidResponseError(BookStackError):
    pass


@dataclass(slots=True)
class BookStackClient:
    base_url: str
    token_id: str
    token_secret: str
    timeout_seconds: float = 10.0
    verify_ssl: bool = True

    @classmethod
    def from_credentials(cls, credentials: dict[str, Any]) -> "BookStackClient":
        verify_ssl = credentials.get("verify_ssl", True)
        if isinstance(verify_ssl, str):
            verify_ssl = verify_ssl.lower() not in {"false", "0"}

        return cls(
            base_url=str(credentials["base_url"]),
            token_id=str(credentials["token_id"]),
            token_secret=str(credentials["token_secret"]),
            timeout_seconds=float(credentials.get("timeout_seconds") or 10),
            verify_ssl=bool(verify_ssl),
        )

    def _api_url(self, path: str) -> str:
        normalized = self.base_url.rstrip("/") + "/"
        return urljoin(normalized, f"api/{path.lstrip('/')}")

    def _session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"Authorization": f"Token {self.token_id}:{self.token_secret}"})
        return session

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self._session().request(
                method=method,
                url=self._api_url(path),
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ServiceUnavailableError("BookStack API unavailable") from exc

        if response.status_code in {401, 403}:
            if response.status_code == 401:
                raise InvalidCredentialsError("Invalid credentials")
            raise PermissionDeniedError("Permission denied")
        if response.status_code == 404:
            raise BookNotFoundError("Resource not found")
        if response.status_code >= 500:
            raise ServiceUnavailableError("BookStack API unavailable")

        if not response.content:
            return {}

        try:
            payload = response.json()
        except ValueError as exc:
            raise InvalidResponseError("Invalid BookStack response") from exc

        if isinstance(payload, dict):
            return payload
        raise InvalidResponseError("Invalid BookStack response")

    def validate_credentials(self) -> None:
        self._request("GET", "system")
