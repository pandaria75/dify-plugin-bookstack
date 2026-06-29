from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookStackClient, InvalidResponseError
from tools.search_pages import normalize_search_page_result


class SearchPagesMappingTestCase(unittest.TestCase):
    def test_normalize_search_page_result_preserves_raw_fields(self):
        raw = {
            "id": 42,
            "name": "Runbook",
            "url": "https://example.test/books/ops/page/runbook",
            "type": "page",
            "preview": "hello",
        }

        normalized = normalize_search_page_result(raw)

        self.assertEqual(normalized["page_id"], 42)
        self.assertEqual(normalized["title"], "Runbook")
        self.assertEqual(normalized["url"], "https://example.test/books/ops/page/runbook")
        self.assertIs(normalized["raw"], raw)

    def test_normalize_search_page_result_falls_back_to_title(self):
        raw = {
            "id": 99,
            "title": "Fallback Title",
            "url": "https://example.test/pages/99",
        }

        normalized = normalize_search_page_result(raw)

        self.assertEqual(normalized["title"], "Fallback Title")


class SearchPagesClientTestCase(unittest.TestCase):
    def test_search_pages_filters_non_page_results(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(
            BookStackClient,
            "_request",
            return_value={
                "data": [
                    {"id": 1, "name": "Page A", "url": "https://example.test/pages/1", "type": "page"},
                    {"id": 2, "name": "Book A", "url": "https://example.test/books/2", "type": "book"},
                    {"id": 3, "name": "Legacy Page", "url": "https://example.test/pages/3"},
                ]
            },
        ) as request:
            results = client.search_pages("ops")

        request.assert_called_once_with("GET", "search", params={"query": "ops"})
        self.assertEqual(results, [
            {"id": 1, "name": "Page A", "url": "https://example.test/pages/1", "type": "page"},
            {"id": 3, "name": "Legacy Page", "url": "https://example.test/pages/3"},
        ])

    def test_search_pages_rejects_invalid_response_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": "not-a-list"}):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client.search_pages("ops")

    def test_search_pages_remains_page_only(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(
            BookStackClient,
            "_request",
            return_value={
                "data": [
                    {"id": 1, "name": "Page A", "type": "page"},
                    {"id": 2, "name": "Shelf A", "type": "bookshelf"},
                ],
                "total": 2,
            },
        ):
            results = client.search_pages("ops")

        self.assertEqual(results, [{"id": 1, "name": "Page A", "type": "page"}])


if __name__ == "__main__":
    unittest.main()
