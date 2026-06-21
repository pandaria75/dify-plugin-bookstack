from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookNotFoundError, BookStackClient, ChapterNotFoundError
from tools.create_page import normalize_created_page_result


class CreatePageMappingTestCase(unittest.TestCase):
    def test_normalize_created_page_result_returns_required_fields_and_raw(self):
        raw = {
            "id": 12,
            "name": "Ops Runbook",
            "url": "https://example.test/books/ops/page/ops-runbook",
            "slug": "ops-runbook",
        }

        normalized = normalize_created_page_result(raw)

        self.assertEqual(normalized["page_id"], 12)
        self.assertEqual(normalized["title"], "Ops Runbook")
        self.assertEqual(normalized["url"], "https://example.test/books/ops/page/ops-runbook")
        self.assertEqual(normalized["action"], "created")
        self.assertIs(normalized["raw"], raw)


class CreatePageClientTestCase(unittest.TestCase):
    def test_create_page_allows_book_root_payload(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 12}) as request:
            result = client.create_page(
                title="Ops Runbook",
                markdown="# Runbook",
                tags=[{"name": "ops", "value": ""}, {"name": "runbook", "value": ""}],
                book_id="7",
            )

        request.assert_called_once_with(
            "POST",
            "pages",
            json={
                "name": "Ops Runbook",
                "markdown": "# Runbook",
                "tags": [{"name": "ops", "value": ""}, {"name": "runbook", "value": ""}],
                "book_id": "7",
            },
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )
        self.assertEqual(result, {"id": 12})

    def test_create_page_prefers_chapter_not_found_mapping(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 13}) as request:
            result = client.create_page(
                title="Ops Runbook",
                markdown="# Runbook",
                chapter_id="11",
                book_id="7",
            )

        request.assert_called_once_with(
            "POST",
            "pages",
            json={
                "name": "Ops Runbook",
                "markdown": "# Runbook",
                "book_id": "7",
                "chapter_id": "11",
            },
            not_found_error=ChapterNotFoundError,
            not_found_message="Chapter not found",
        )
        self.assertEqual(result, {"id": 13})


if __name__ == "__main__":
    unittest.main()
