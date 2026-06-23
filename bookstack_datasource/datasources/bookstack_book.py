from __future__ import annotations

from collections.abc import Generator, Mapping
from typing import Any

from dify_plugin.entities.datasource import (
    DatasourceGetPagesResponse,
    DatasourceMessage,
    GetOnlineDocumentPageContentRequest,
    OnlineDocumentInfo,
    OnlineDocumentPage,
)
from dify_plugin.interfaces.datasource.online_document import (
    OnlineDocumentDatasource,
)

try:
    from ..bookstack_client import BookStackClient
    from ._metadata import build_metadata, normalize_id, page_id, page_title
except ImportError:  # Dify installed-runtime source loading fallback
    from bookstack_client import BookStackClient
    from datasources._metadata import build_metadata, normalize_id, page_id, page_title


class BookStackBookDatasource(OnlineDocumentDatasource):
    _PAGE_BATCH_SIZE = 100

    @staticmethod
    def _normalize_book_id(value: Any) -> str:
        return normalize_id(value, "book_id")

    @staticmethod
    def _normalize_page_id(value: Any) -> str:
        return normalize_id(value, "page_id")

    def _book_id_from_parameters(self, datasource_parameters: Mapping[str, Any]) -> str:
        return self._normalize_book_id(datasource_parameters.get("book_id"))

    def _content_identity_from_request(
        self, page: GetOnlineDocumentPageContentRequest
    ) -> tuple[str, str | None]:
        page_id: str | None = None
        parent_id: str | None = None

        for candidate in (page, getattr(page, "page", None)):
            if candidate is None:
                continue

            if page_id is None:
                for attr in ("page_id", "id"):
                    if hasattr(candidate, attr):
                        value = getattr(candidate, attr)
                        if str(value or "").strip():
                            page_id = self._normalize_page_id(value)
                            break

            if parent_id is None:
                for attr in ("parent_id", "chapter_id", "book_id"):
                    if hasattr(candidate, attr):
                        value = getattr(candidate, attr)
                        if str(value or "").strip():
                            parent_id = str(value).strip()
                            break

        if page_id is None:
            raise ValueError("page_id is required")

        return page_id, parent_id

    def _build_client(self) -> BookStackClient:
        return BookStackClient.from_credentials(self.runtime.credentials)

    @staticmethod
    def _page_id(raw_page: Mapping[str, Any]) -> str:
        return page_id(raw_page)

    @classmethod
    def _page_title(cls, raw_page: Mapping[str, Any]) -> str:
        return page_title(raw_page)

    @staticmethod
    def _book_parent_id(raw_page: Mapping[str, Any], fallback_book_id: str) -> str:
        chapter = raw_page.get("chapter")
        if isinstance(chapter, Mapping):
            chapter_id = str(chapter.get("id") or "").strip()
            if chapter_id:
                return chapter_id

        chapter_id = str(raw_page.get("chapter_id") or "").strip()
        if chapter_id:
            return chapter_id

        book = raw_page.get("book")
        if isinstance(book, Mapping):
            book_id = str(book.get("id") or "").strip()
            if book_id:
                return book_id

        book_id = str(raw_page.get("book_id") or "").strip()
        if book_id:
            return book_id

        return fallback_book_id

    @staticmethod
    def _workspace_name(raw_pages: list[Mapping[str, Any]], book_id: str) -> str:
        for raw_page in raw_pages:
            book = raw_page.get("book")
            if isinstance(book, Mapping):
                name = str(book.get("name") or "").strip()
                if name:
                    return name

        return f"Book {book_id}"

    @classmethod
    def _build_page_entry(cls, raw_page: Mapping[str, Any], book_id: str) -> OnlineDocumentPage:
        return OnlineDocumentPage(
            page_id=cls._page_id(raw_page),
            page_name=cls._page_title(raw_page),
            page_icon=None,
            type="page",
            last_edited_time="",
            parent_id=cls._book_parent_id(raw_page, book_id),
        )

    @classmethod
    def _build_content_payload(
        cls,
        raw_page: Mapping[str, Any],
        fallback_parent_id: str | None = None,
        fallback_page_id: str | None = None,
    ) -> dict[str, Any]:
        parent_id = cls._book_parent_id(raw_page, fallback_parent_id or "")
        sync_source_id = (
            fallback_parent_id
            or cls._book_parent_id(raw_page, "")
            or cls._page_id(raw_page)
            or fallback_page_id
        )
        return build_metadata(
            raw_page,
            sync_scope="book",
            sync_source_id=sync_source_id,
            parent_id=parent_id or None,
            fallback_page_id=fallback_page_id,
        )

    @classmethod
    def _build_content_message(
        cls,
        raw_page: Mapping[str, Any],
        fallback_parent_id: str | None = None,
        fallback_page_id: str | None = None,
    ) -> DatasourceMessage:
        payload = cls._build_content_payload(raw_page, fallback_parent_id, fallback_page_id)
        content = payload.get("content") or ""
        return DatasourceMessage(
            type=DatasourceMessage.MessageType.TEXT,
            message=DatasourceMessage.TextMessage(text=content),
            meta={key: value for key, value in payload.items() if key != "content"},
        )

    def _list_book_pages(self, client: BookStackClient, book_id: str) -> list[Mapping[str, Any]]:
        raw_pages: list[Mapping[str, Any]] = []
        offset = 0

        while True:
            payload = client.list_pages(
                book_id=book_id,
                count=self._PAGE_BATCH_SIZE,
                offset=offset,
            )
            batch = payload.get("data", [])
            raw_pages.extend(batch)

            if not batch:
                break

            total = payload.get("total")
            if isinstance(total, int) and len(raw_pages) >= total:
                break

            if isinstance(total, int):
                offset += len(batch)
                continue

            if len(batch) < self._PAGE_BATCH_SIZE:
                break

            offset += len(batch)

        return raw_pages

    def _get_pages(
        self, datasource_parameters: Mapping[str, Any]
    ) -> DatasourceGetPagesResponse:
        book_id = self._book_id_from_parameters(datasource_parameters)
        client = self._build_client()
        raw_pages = self._list_book_pages(client, book_id)
        pages = [self._build_page_entry(raw_page, book_id) for raw_page in raw_pages]

        return DatasourceGetPagesResponse(
            result=[
                OnlineDocumentInfo(
                    workspace_id=book_id,
                    workspace_name=self._workspace_name(raw_pages, book_id),
                    workspace_icon="",
                    total=len(pages),
                    pages=pages,
                )
            ]
        )

    def _get_content(
        self, page: GetOnlineDocumentPageContentRequest
    ) -> Generator[Any, None, None]:
        page_id, parent_id = self._content_identity_from_request(page)
        client = self._build_client()
        raw_page = client.get_page(page_id)
        yield self._build_content_message(raw_page, parent_id, page_id)
