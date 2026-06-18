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


def normalize_book_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "book_id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "description": raw.get("description"),
        "url": raw.get("url"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "raw": raw,
    }


class ListBooksTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        count = tool_parameters.get("count")
        offset = tool_parameters.get("offset")

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            payload = client.list_books(count=count, offset=offset)
        except BookStackError as exc:
            yield self.create_text_message(f"success=false\nerror={exc}")
            return

        raw_books = payload.get("data", [])
        response = {
            "books": [normalize_book_result(item) for item in raw_books],
            "count": len(raw_books),
        }
        if "total" in payload:
            response["total"] = payload.get("total")

        yield self.create_json_message(response)
