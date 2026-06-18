from __future__ import annotations

from collections.abc import Generator
from typing import Any

try:
    from dify_plugin import Tool
    from dify_plugin.entities.tool import ToolInvokeMessage
except ImportError:  # pragma: no cover - allows helper imports in unit tests
    Tool = object
    ToolInvokeMessage = Any

from bookstack_client import BookStackClient, BookStackError


def normalize_page_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "markdown": raw.get("markdown") or raw.get("body") or "",
        "book_id": raw.get("book_id"),
        "chapter_id": raw.get("chapter_id"),
        "slug": raw.get("slug"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "created_by": raw.get("created_by"),
        "updated_by": raw.get("updated_by"),
        "raw": raw,
    }


class GetPageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        page_id = str(tool_parameters.get("page_id", "")).strip()
        if not page_id:
            yield self.create_text_message("success=false\nerror=page_id is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_page = client.get_page(page_id)
        except BookStackError as exc:
            yield self.create_text_message(f"success=false\nerror={exc}")
            return

        yield self.create_json_message(normalize_page_result(raw_page))
