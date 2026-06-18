from __future__ import annotations

from typing import Any


def normalize_tags(value: Any) -> list[str] | None:
    if value in {None, ""}:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        return [text]

    normalized: list[str] = []
    if isinstance(value, list):
        for item in value:
            text = str(item).strip()
            if text:
                normalized.append(text)
    else:
        text = str(value).strip()
        if text:
            normalized.append(text)

    return normalized or None
