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


class BookStackPageDatasource(OnlineDocumentDatasource):
    @staticmethod
    def _normalize_page_id(value: Any) -> str:
        return normalize_id(value, "page_id")

    def _page_id_from_parameters(self, datasource_parameters: Mapping[str, Any]) -> str:
        return self._normalize_page_id(datasource_parameters.get("page_id"))

    def _page_id_from_request(self, page: GetOnlineDocumentPageContentRequest) -> str:
        for attr in ("page_id", "id"):
            if hasattr(page, attr):
                value = getattr(page, attr)
                if str(value or "").strip():
                    return self._normalize_page_id(value)

        if hasattr(page, "page"):
            nested_page = getattr(page, "page")
            for attr in ("page_id", "id"):
                if hasattr(nested_page, attr):
                    value = getattr(nested_page, attr)
                    if str(value or "").strip():
                        return self._normalize_page_id(value)

        raise ValueError("page_id is required")

    def _build_client(self) -> BookStackClient:
        return BookStackClient.from_credentials(self.runtime.credentials)

    @staticmethod
    def _build_page_stub(raw_page: Mapping[str, Any]) -> OnlineDocumentInfo:
        normalized_page_id = page_id(raw_page)
        title = page_title(raw_page)

        return OnlineDocumentInfo(
            workspace_id=normalized_page_id,
            workspace_name=title,
            workspace_icon="",
            total=1,
            pages=[
                OnlineDocumentPage(
                    page_id=normalized_page_id,
                    page_name=title,
                    page_icon=None,
                    type="page",
                    last_edited_time="",
                    parent_id=None,
                )
            ],
        )

    @staticmethod
    def _build_content_payload(
        raw_page: Mapping[str, Any], fallback_page_id: str | None = None
    ) -> dict[str, Any]:
        return build_metadata(
            raw_page,
            sync_scope="page",
            sync_source_id=fallback_page_id or page_id(raw_page),
            parent_id=None,
            fallback_page_id=fallback_page_id,
        )

    @staticmethod
    def _build_content_message(
        raw_page: Mapping[str, Any], fallback_page_id: str | None = None
    ) -> DatasourceMessage:
        payload = BookStackPageDatasource._build_content_payload(raw_page, fallback_page_id)
        content = payload.get("content") or ""
        return DatasourceMessage(
            type=DatasourceMessage.MessageType.TEXT,
            message=DatasourceMessage.TextMessage(text=content),
            meta={key: value for key, value in payload.items() if key != "content"},
        )

    def _get_pages(
        self, datasource_parameters: Mapping[str, Any]
    ) -> DatasourceGetPagesResponse:
        client = self._build_client()
        raw_page = client.get_page(self._page_id_from_parameters(datasource_parameters))
        return DatasourceGetPagesResponse(result=[self._build_page_stub(raw_page)])

    def _get_content(
        self, page: GetOnlineDocumentPageContentRequest
    ) -> Generator[Any, None, None]:
        client = self._build_client()
        request_page_id = self._page_id_from_request(page)
        raw_page = client.get_page(request_page_id)
        yield self._build_content_message(raw_page, request_page_id)
