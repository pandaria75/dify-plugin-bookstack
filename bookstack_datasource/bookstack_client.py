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


def _invalid_credentials() -> InvalidCredentialsError:
    return InvalidCredentialsError("Invalid credentials")


def _service_unavailable() -> ServiceUnavailableError:
    return ServiceUnavailableError("BookStack API unavailable")


def _invalid_response() -> InvalidResponseError:
    return InvalidResponseError("Invalid BookStack response")


@dataclass(slots=True)
class BookStackClient:

    base_url: str

    token_id: str

    token_secret: str

    timeout_seconds: float = 10.0

    verify_ssl: bool = True

    @classmethod
    def from_credentials(cls, credentials: dict[str, Any]) -> "BookStackClient":
        base_url = cls._require_credential(credentials, "base_url")
        token_id = cls._require_credential(credentials, "token_id")
        token_secret = cls._require_credential(credentials, "token_secret")

        return cls(
            base_url=base_url,
            token_id=token_id,
            token_secret=token_secret,
            timeout_seconds=cls._parse_timeout(credentials.get("timeout_seconds")),
            verify_ssl=cls._parse_verify_ssl(credentials.get("verify_ssl", True)),
        )

    @staticmethod
    def _require_credential(credentials: dict[str, Any], key: str) -> str:
        value = credentials.get(key)
        if value is None:
            raise _invalid_credentials()

        text = str(value).strip()
        if not text:
            raise _invalid_credentials()

        return text

    @staticmethod
    def _parse_timeout(value: Any) -> float:
        if value in {None, ""}:
            return 10.0

        try:
            timeout = float(value)
        except (TypeError, ValueError) as exc:
            raise _invalid_credentials() from exc

        if timeout <= 0:
            raise _invalid_credentials()

        return timeout

    @staticmethod
    def _parse_verify_ssl(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1"}:
                return True
            if normalized in {"false", "0"}:
                return False
            raise _invalid_credentials()
        if isinstance(value, (int, float)):
            if value == 1:
                return True
            if value == 0:
                return False
            raise _invalid_credentials()
        raise _invalid_credentials()

    def _api_url(self, path: str) -> str:
        normalized = self.base_url.rstrip("/") + "/"
        return urljoin(normalized, f"api/{path.lstrip('/')}")

    def _session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"Authorization": f"Token {self.token_id}:{self.token_secret}"})
        return session

    def _request(
        self,
        method: str,
        path: str,
        *,
        not_found_error: type[BookStackError] = BookNotFoundError,
        not_found_message: str = "Resource not found",
        **kwargs: Any,
    ) -> dict[str, Any]:
        try:
            response = self._session().request(
                method=method,
                url=self._api_url(path),
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
                **kwargs,
            )
        except (requests.Timeout, requests.ConnectionError, requests.RequestException) as exc:
            raise _service_unavailable() from exc

        if response.status_code in {401, 403}:
            if response.status_code == 401:
                raise _invalid_credentials()
            raise PermissionDeniedError("Permission denied")
        if response.status_code == 404:
            raise not_found_error(not_found_message)
        if response.status_code in {400, 422}:
            raise _invalid_response()
        if response.status_code == 429 or response.status_code >= 500:
            raise _service_unavailable()
        if response.status_code >= 400:
            raise _service_unavailable()

        if not response.content:
            return {}

        try:
            payload = response.json()
        except ValueError as exc:
            raise _invalid_response() from exc

        if isinstance(payload, dict):
            return payload
        raise _invalid_response()

    def validate_credentials(self) -> None:
        self._request("GET", "system")

    def get_page(self, page_id: Any) -> dict[str, Any]:
        return self._request(
            "GET",
            f"pages/{page_id}",
            not_found_error=PageNotFoundError,
            not_found_message="Page not found",
        )
