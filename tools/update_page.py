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
from tools.page_inputs import normalize_tags


def normalize_updated_page_result(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": raw.get("id"),
        "title": raw.get("name") or raw.get("title"),
        "url": raw.get("url"),
        "action": "updated",
        "raw": raw,
    }


class UpdatePageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        page_id = str(tool_parameters.get("page_id", "")).strip()
        title = tool_parameters.get("title")
        markdown = tool_parameters.get("markdown")
        book_id = tool_parameters.get("book_id")
        chapter_id = tool_parameters.get("chapter_id")
        tags = normalize_tags(tool_parameters.get("tags")) if "tags" in tool_parameters else None

        if not page_id:
            yield self.create_text_message("success=false\nerror=page_id is required")
            return

        updates: dict[str, Any] = {}
        if title is not None:
            normalized_title = str(title).strip()
            if not normalized_title:
                yield self.create_text_message("success=false\nerror=title must not be empty")
                return
            updates["title"] = normalized_title
        if markdown is not None:
            updates["markdown"] = str(markdown)
        if "tags" in tool_parameters:
            updates["tags"] = tags
        if book_id not in {None, ""}:
            updates["book_id"] = book_id
        if chapter_id not in {None, ""}:
            updates["chapter_id"] = chapter_id

        if not updates:
            yield self.create_text_message("success=false\nerror=at least one update field is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            raw_page = client.update_page(page_id, **updates)
        except BookStackError as exc:
            yield self.create_text_message(f"success=false\nerror={exc}")
            return

        yield self.create_json_message(normalize_updated_page_result(raw_page))
