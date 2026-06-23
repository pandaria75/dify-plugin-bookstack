from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def normalize_id(value: Any, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def page_id(raw_page: Mapping[str, Any]) -> str:
    return str(raw_page.get("id") or "").strip()


def page_title(raw_page: Mapping[str, Any]) -> str:
    normalized_page_id = page_id(raw_page)
    return raw_page.get("name") or raw_page.get("title") or f"Page {normalized_page_id}"


def nested_entity_id(raw_page: Mapping[str, Any], entity_name: str) -> str | None:
    entity = raw_page.get(entity_name)
    if isinstance(entity, Mapping):
        normalized = str(entity.get("id") or "").strip()
        if normalized:
            return normalized

    normalized = str(raw_page.get(f"{entity_name}_id") or "").strip()
    return normalized or None


def page_content_and_format(raw_page: Mapping[str, Any]) -> tuple[str, str | None]:
    for field_name, content_format in (("html", "html"), ("markdown", "markdown"), ("body", "body")):
        value = raw_page.get(field_name)
        if isinstance(value, str) and value:
            return value, content_format
    return "", None


def normalize_tags(raw_page: Mapping[str, Any]) -> list[str]:
    raw_tags = raw_page.get("tags")
    if not isinstance(raw_tags, Sequence) or isinstance(raw_tags, (str, bytes)):
        return []

    normalized_tags: list[str] = []
    for raw_tag in raw_tags:
        if isinstance(raw_tag, str):
            tag = raw_tag.strip()
        elif isinstance(raw_tag, Mapping):
            tag = str(raw_tag.get("name") or raw_tag.get("value") or "").strip()
        else:
            tag = str(raw_tag or "").strip()

        if tag:
            normalized_tags.append(tag)

    return normalized_tags


def build_metadata(
    raw_page: Mapping[str, Any],
    *,
    sync_scope: str,
    sync_source_id: str | None,
    parent_id: str | None = None,
    fallback_page_id: str | None = None,
) -> dict[str, Any]:
    content, content_format = page_content_and_format(raw_page)
    source_url = raw_page.get("url") or None
    normalized_page_id = page_id(raw_page) or fallback_page_id or None
    normalized_sync_source_id = sync_source_id or normalized_page_id

    return {
        "source": "bookstack",
        "sync_scope": sync_scope,
        "sync_source_id": normalized_sync_source_id,
        "page_id": normalized_page_id,
        "bookstack_page_id": normalized_page_id,
        "bookstack_book_id": nested_entity_id(raw_page, "book"),
        "bookstack_chapter_id": nested_entity_id(raw_page, "chapter"),
        "title": page_title(raw_page),
        "url": source_url,
        "source_url": source_url,
        "tags": normalize_tags(raw_page),
        "created_at": raw_page.get("created_at") or None,
        "updated_at": raw_page.get("updated_at") or None,
        "content_format": content_format,
        "parent_id": parent_id,
        "content": content,
    }
