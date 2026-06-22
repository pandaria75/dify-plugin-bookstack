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

from ..bookstack_client import BookStackClient


class BookStackPageDatasource(OnlineDocumentDatasource):
    @staticmethod
    def _normalize_page_id(value: Any) -> str:
        page_id = str(value or "").strip()
        if not page_id:
            raise ValueError("page_id is required")
        return page_id

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
        page_id = str(raw_page.get("id") or "").strip()
        title = raw_page.get("name") or raw_page.get("title") or f"Page {page_id}"

        return OnlineDocumentInfo(
            workspace_id=page_id,
            workspace_name=title,
            workspace_icon="",
            total=1,
            pages=[
                OnlineDocumentPage(
                    page_id=page_id,
                    page_name=title,
                    page_icon=None,
                    type="page",
                    last_edited_time="",
                    parent_id=None,
                )
            ],
        )

    @staticmethod
    def _build_content_payload(raw_page: Mapping[str, Any]) -> dict[str, Any]:
        page_id = str(raw_page.get("id") or "").strip()
        title = raw_page.get("name") or raw_page.get("title") or f"Page {page_id}"

        return {
            "page_id": page_id,
            "title": title,
            "content": raw_page.get("html") or raw_page.get("markdown") or raw_page.get("body") or "",
            "source_url": raw_page.get("url") or "",
        }

    @staticmethod
    def _build_content_message(raw_page: Mapping[str, Any]) -> DatasourceMessage:
        return DatasourceMessage(
            type=DatasourceMessage.MessageType.JSON,
            message=DatasourceMessage.JsonMessage(
                json_object=BookStackPageDatasource._build_content_payload(raw_page)
            ),
            meta=None,
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
        raw_page = client.get_page(self._page_id_from_request(page))
        yield self._build_content_message(raw_page)
