from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookStackClient, InvalidResponseError, PageNotFoundError
from tools.get_page import normalize_page_result


class GetPageMappingTestCase(unittest.TestCase):
    def test_normalize_page_result_returns_required_fields_and_raw(self):
        raw = {
            "id": 42,
            "name": "Runbook",
            "url": "https://example.test/books/ops/page/runbook",
            "markdown": "# Runbook",
            "book_id": 7,
            "chapter_id": 11,
            "slug": "runbook",
            "created_at": "2026-06-17T00:00:00Z",
            "updated_at": "2026-06-17T01:00:00Z",
            "created_by": {"id": 2, "name": "Alice"},
            "updated_by": {"id": 3, "name": "Bob"},
        }

        normalized = normalize_page_result(raw)

        self.assertEqual(normalized["page_id"], 42)
        self.assertEqual(normalized["title"], "Runbook")
        self.assertEqual(normalized["url"], "https://example.test/books/ops/page/runbook")
        self.assertEqual(normalized["markdown"], "# Runbook")
        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["chapter_id"], 11)
        self.assertEqual(normalized["slug"], "runbook")
        self.assertIs(normalized["raw"], raw)

    def test_normalize_page_result_falls_back_to_body_and_title(self):
        raw = {
            "id": 99,
            "title": "Fallback Title",
            "url": "https://example.test/pages/99",
            "body": "Legacy body",
        }

        normalized = normalize_page_result(raw)

        self.assertEqual(normalized["title"], "Fallback Title")
        self.assertEqual(normalized["markdown"], "Legacy body")


class GetPageClientTestCase(unittest.TestCase):
    def test_get_page_uses_page_not_found_mapping(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 42}) as request:
            result = client.get_page(42)

        request.assert_called_once_with(
            "GET",
            "pages/42",
            not_found_error=PageNotFoundError,
            not_found_message="Page not found",
        )
        self.assertEqual(result, {"id": 42})

    def test_get_page_rejects_invalid_response_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={}):
            result = client.get_page(42)

        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
