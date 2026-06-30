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


class ShelfNotFoundError(BookStackError):
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


def normalize_find_match(value: Any) -> str:
    match = str(value or "").strip().lower()
    if match not in {"exact", "like"}:
        raise ValueError("match must be one of: exact, like")
    return match


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

    @staticmethod
    def _require_object_list(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise _invalid_response()

        items: list[dict[str, Any]] = []
        for item in value:
            if not isinstance(item, dict):
                raise _invalid_response()
            items.append(item)

        return items

    @staticmethod
    def _build_list_params(**params: Any) -> dict[str, Any]:
        return {key: value for key, value in params.items() if value is not None}

    @staticmethod
    def _build_name_filter_params(name: Any, match: str, **params: Any) -> dict[str, Any]:
        match = normalize_find_match(match)
        if match == "exact":
            filter_key = "filter[name:eq]"
            filter_value = name
        else:
            filter_key = "filter[name:like]"
            filter_value = f"%{name}%"

        return BookStackClient._build_list_params(**{filter_key: filter_value}, **params)

    def _list_endpoint(
        self,
        path: str,
        *,
        not_found_error: type[BookStackError] | None = None,
        not_found_message: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        filtered_params = self._build_list_params(**params)

        request_kwargs: dict[str, Any] = {}
        if filtered_params:
            request_kwargs["params"] = filtered_params
        if not_found_error is not None:
            request_kwargs["not_found_error"] = not_found_error
        if not_found_message is not None:
            request_kwargs["not_found_message"] = not_found_message

        payload = self._request("GET", path, **request_kwargs)
        self._require_object_list(payload.get("data"))
        return payload

    def _search(self, query: str) -> dict[str, Any]:
        payload = self._request("GET", "search", params={"query": query})
        self._require_object_list(payload.get("data"))
        return payload

    def search_content(
        self,
        query: str,
        *,
        types: list[str] | None = None,
    ) -> dict[str, Any]:
        payload = self._search(query)
        data = payload.get("data", [])

        if types is None:
            return payload

        allowed_types = set(types)
        filtered_data: list[dict[str, Any]] = []
        for item in data:
            item_type = item.get("type")
            if item_type in allowed_types:
                filtered_data.append(item)

        return {
            **payload,
            "data": filtered_data,
        }

    def search_pages(self, query: str) -> list[dict[str, Any]]:
        payload = self._search(query)
        data = payload.get("data", [])

        page_results: list[dict[str, Any]] = []
        for item in data:
            if item.get("type") not in {None, "page"}:
                continue
            page_results.append(item)

        return page_results

    def list_books(self, count: Any | None = None, offset: Any | None = None) -> dict[str, Any]:
        return self._list_endpoint("books", count=count, offset=offset)

    def list_shelves(self, count: Any | None = None, offset: Any | None = None) -> dict[str, Any]:
        return self._list_endpoint("shelves", count=count, offset=offset)

    def find_books(
        self,
        name: Any,
        *,
        match: str,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        return self._list_endpoint(
            "books",
            **self._build_name_filter_params(name, match, count=count, offset=offset),
        )

    def find_shelves(
        self,
        name: Any,
        *,
        match: str,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        return self._list_endpoint(
            "shelves",
            **self._build_name_filter_params(name, match, count=count, offset=offset),
        )

    def find_chapters(
        self,
        name: Any,
        *,
        match: str,
        book_id: Any | None = None,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        return self._list_endpoint(
            "chapters",
            **self._build_name_filter_params(
                name,
                match,
                **self._build_list_params(
                    **{"filter[book_id:eq]": book_id},
                    count=count,
                    offset=offset,
                ),
            ),
        )

    def find_pages(
        self,
        name: Any,
        *,
        match: str,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        return self._list_endpoint(
            "pages",
            **self._build_name_filter_params(
                name,
                match,
                **self._build_list_params(
                    **{
                        "filter[book_id:eq]": book_id,
                        "filter[chapter_id:eq]": chapter_id,
                    },
                    count=count,
                    offset=offset,
                ),
            ),
        )

    def list_pages(
        self,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if book_id is not None:
            params["filter[book_id:eq]"] = book_id
        if chapter_id is not None:
            params["filter[chapter_id:eq]"] = chapter_id
        if count is not None:
            params["count"] = count
        if offset is not None:
            params["offset"] = offset

        request_kwargs: dict[str, Any] = {}
        if params:
            request_kwargs["params"] = params

        payload = self._request("GET", "pages", **request_kwargs)
        data = payload.get("data")

        if not isinstance(data, list):
            raise InvalidResponseError("Invalid BookStack response")

        return payload

    def list_chapters(
        self,
        book_id: Any | None = None,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        return self._list_endpoint(
            "chapters",
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
            **self._build_list_params(
                **{"filter[book_id:eq]": book_id},
                count=count,
                offset=offset,
            ),
        )

    def get_page(self, page_id: Any) -> dict[str, Any]:
        return self._request(
            "GET",
            f"pages/{page_id}",
            not_found_error=PageNotFoundError,
            not_found_message="Page not found",
        )

    def get_book(self, book_id: Any) -> dict[str, Any]:
        return self._request(
            "GET",
            f"books/{book_id}",
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )

    def get_chapter(self, chapter_id: Any) -> dict[str, Any]:
        return self._request(
            "GET",
            f"chapters/{chapter_id}",
            not_found_error=ChapterNotFoundError,
            not_found_message="Chapter not found",
        )

    def get_shelf(self, shelf_id: Any) -> dict[str, Any]:
        return self._request(
            "GET",
            f"shelves/{shelf_id}",
            not_found_error=ShelfNotFoundError,
            not_found_message="Shelf not found",
        )

    @staticmethod
    def _build_page_payload(
        *,
        title: Any | None = None,
        markdown: Any | None = None,
        tags: Any | None = None,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}

        if title is not None:
            payload["name"] = title
        if markdown is not None:
            payload["markdown"] = markdown
        if tags is not None:
            payload["tags"] = tags
        if book_id is not None:
            payload["book_id"] = book_id
        if chapter_id is not None:
            payload["chapter_id"] = chapter_id

        return payload

    @staticmethod
    def _build_resource_payload(**fields: Any) -> dict[str, Any]:
        return {key: value for key, value in fields.items() if value is not None}

    @staticmethod
    def _build_book_payload(
        *,
        name: Any | None = None,
        description: Any | None = None,
        description_html: Any | None = None,
        tags: Any | None = None,
    ) -> dict[str, Any]:
        return BookStackClient._build_resource_payload(
            name=name,
            description=description,
            description_html=description_html,
            tags=tags,
        )

    @staticmethod
    def _build_chapter_payload(
        *,
        book_id: Any | None = None,
        name: Any | None = None,
        description: Any | None = None,
        description_html: Any | None = None,
        tags: Any | None = None,
        priority: Any | None = None,
    ) -> dict[str, Any]:
        return BookStackClient._build_resource_payload(
            book_id=book_id,
            name=name,
            description=description,
            description_html=description_html,
            tags=tags,
            priority=priority,
        )

    @staticmethod
    def _build_shelf_payload(
        *,
        name: Any | None = None,
        description: Any | None = None,
        description_html: Any | None = None,
        books: Any | None = None,
        tags: Any | None = None,
    ) -> dict[str, Any]:
        return BookStackClient._build_resource_payload(
            name=name,
            description=description,
            description_html=description_html,
            books=books,
            tags=tags,
        )

    def create_page(
        self,
        *,
        title: Any,
        markdown: Any,
        tags: Any | None = None,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
    ) -> dict[str, Any]:
        not_found_error: type[BookStackError]
        not_found_message: str

        if chapter_id is not None:
            not_found_error = ChapterNotFoundError
            not_found_message = "Chapter not found"
        else:
            not_found_error = BookNotFoundError
            not_found_message = "Book not found"

        return self._request(
            "POST",
            "pages",
            json=self._build_page_payload(
                title=title,
                markdown=markdown,
                tags=tags,
                book_id=book_id,
                chapter_id=chapter_id,
            ),
            not_found_error=not_found_error,
            not_found_message=not_found_message,
        )

    def update_page(
        self,
        page_id: Any,
        *,
        title: Any | None = None,
        markdown: Any | None = None,
        tags: Any | None = None,
        book_id: Any | None = None,
        chapter_id: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"pages/{page_id}",
            json=self._build_page_payload(
                title=title,
                markdown=markdown,
                tags=tags,
                book_id=book_id,
                chapter_id=chapter_id,
            ),
            not_found_error=PageNotFoundError,
            not_found_message="Page not found",
        )

    def create_book(
        self,
        *,
        name: Any,
        description: Any | None = None,
        description_html: Any | None = None,
        tags: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "books",
            json=self._build_book_payload(
                name=name,
                description=description,
                description_html=description_html,
                tags=tags,
            ),
        )

    def update_book(
        self,
        book_id: Any,
        *,
        name: Any | None = None,
        description: Any | None = None,
        description_html: Any | None = None,
        tags: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"books/{book_id}",
            json=self._build_book_payload(
                name=name,
                description=description,
                description_html=description_html,
                tags=tags,
            ),
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )

    def create_chapter(
        self,
        *,
        book_id: Any,
        name: Any,
        description: Any | None = None,
        description_html: Any | None = None,
        tags: Any | None = None,
        priority: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "chapters",
            json=self._build_chapter_payload(
                book_id=book_id,
                name=name,
                description=description,
                description_html=description_html,
                tags=tags,
                priority=priority,
            ),
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )

    def update_chapter(
        self,
        chapter_id: Any,
        *,
        book_id: Any | None = None,
        name: Any | None = None,
        description: Any | None = None,
        description_html: Any | None = None,
        tags: Any | None = None,
        priority: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"chapters/{chapter_id}",
            json=self._build_chapter_payload(
                book_id=book_id,
                name=name,
                description=description,
                description_html=description_html,
                tags=tags,
                priority=priority,
            ),
            not_found_error=ChapterNotFoundError,
            not_found_message="Chapter not found",
        )

    def create_shelf(
        self,
        *,
        name: Any,
        description: Any | None = None,
        description_html: Any | None = None,
        books: Any | None = None,
        tags: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "shelves",
            json=self._build_shelf_payload(
                name=name,
                description=description,
                description_html=description_html,
                books=books,
                tags=tags,
            ),
        )

    def update_shelf(
        self,
        shelf_id: Any,
        *,
        name: Any | None = None,
        description: Any | None = None,
        description_html: Any | None = None,
        books: Any | None = None,
        tags: Any | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"shelves/{shelf_id}",
            json=self._build_shelf_payload(
                name=name,
                description=description,
                description_html=description_html,
                books=books,
                tags=tags,
            ),
            not_found_error=ShelfNotFoundError,
            not_found_message="Shelf not found",
        )

    def list_tag_names(self, count: Any | None = None, offset: Any | None = None) -> dict[str, Any]:
        return self._list_endpoint("tags/names", count=count, offset=offset)

    def list_tag_values(
        self,
        name: Any,
        *,
        count: Any | None = None,
        offset: Any | None = None,
    ) -> dict[str, Any]:
        return self._list_endpoint("tags/values-for-name", name=name, count=count, offset=offset)
