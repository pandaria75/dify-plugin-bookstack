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
from tools.create_page import normalize_created_page_result
from tools.page_inputs import normalize_tags
from tools.update_page import normalize_updated_page_result


def _normalize_title(value: Any) -> str:
    return str(value or "").strip()


def _page_title(raw: dict[str, Any]) -> str:
    return _normalize_title(raw.get("name") or raw.get("title"))


def _page_location_matches(raw: dict[str, Any], *, book_id: Any | None, chapter_id: Any | None) -> bool:
    if book_id not in {None, ""}:
        raw_book_id = raw.get("book_id")
        if raw_book_id is not None and str(raw_book_id) != str(book_id):
            return False
    if chapter_id not in {None, ""}:
        raw_chapter_id = raw.get("chapter_id")
        if raw_chapter_id is not None and str(raw_chapter_id) != str(chapter_id):
            return False
    return True


def _match_exact_title(
    raw_results: list[dict[str, Any]],
    *,
    title: str,
    book_id: Any | None,
    chapter_id: Any | None,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for raw in raw_results:
        if not isinstance(raw, dict):
            continue
        if _page_title(raw) != title:
            continue
        if not _page_location_matches(raw, book_id=book_id, chapter_id=chapter_id):
            continue
        matches.append(raw)
    return matches


class PublishPageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        title = _normalize_title(tool_parameters.get("title"))
        markdown = str(tool_parameters.get("markdown", "")).strip()
        page_id = _normalize_title(tool_parameters.get("page_id"))
        book_id = tool_parameters.get("book_id")
        chapter_id = tool_parameters.get("chapter_id")
        tags = normalize_tags(tool_parameters.get("tags")) if "tags" in tool_parameters else None

        if not title:
            yield self.create_text_message("success=false\nerror=title is required")
            return
        if not markdown:
            yield self.create_text_message("success=false\nerror=markdown is required")
            return

        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)

            if page_id:
                raw_page = client.update_page(
                    page_id,
                    title=title,
                    markdown=markdown,
                    tags=tags,
                    book_id=book_id if book_id not in {None, ""} else None,
                    chapter_id=chapter_id if chapter_id not in {None, ""} else None,
                )
                yield self.create_json_message({"success": True, **normalize_updated_page_result(raw_page)})
                return

            raw_results = client.search_pages(title)
            exact_matches = _match_exact_title(
                raw_results,
                title=title,
                book_id=book_id,
                chapter_id=chapter_id,
            )

            if len(exact_matches) > 1:
                yield self.create_text_message("success=false\nerror=ambiguous title match")
                return

            if len(exact_matches) == 1:
                raw_page = client.update_page(
                    exact_matches[0].get("id"),
                    title=title,
                    markdown=markdown,
                    tags=tags,
                    book_id=book_id if book_id not in {None, ""} else None,
                    chapter_id=chapter_id if chapter_id not in {None, ""} else None,
                )
                yield self.create_json_message({"success": True, **normalize_updated_page_result(raw_page)})
                return

            if book_id in {None, ""} and chapter_id in {None, ""}:
                yield self.create_text_message("success=false\nerror=book_id or chapter_id is required to create a new page")
                return

            raw_page = client.create_page(
                title=title,
                markdown=markdown,
                tags=tags,
                book_id=book_id if book_id not in {None, ""} else None,
                chapter_id=chapter_id if chapter_id not in {None, ""} else None,
            )
            yield self.create_json_message({"success": True, **normalize_created_page_result(raw_page)})
        except BookStackError as exc:
            yield self.create_text_message(f"success=false\nerror={exc}")
