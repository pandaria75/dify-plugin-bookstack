from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookStackClient, InvalidResponseError
from tools.list_pages import normalize_page_list_result


class ListPagesMappingTestCase(unittest.TestCase):
    def test_normalize_page_list_result_preserves_supported_fields(self):
        raw = {
            "id": 13,
            "name": "Incident Guide",
            "slug": "incident-guide",
            "book_id": 7,
            "chapter_id": 11,
            "url": "https://example.test/pages/incident-guide",
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "extra": "keep-in-raw",
        }

        normalized = normalize_page_list_result(raw)

        self.assertEqual(normalized["page_id"], 13)
        self.assertEqual(normalized["title"], "Incident Guide")
        self.assertEqual(normalized["slug"], "incident-guide")
        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["chapter_id"], 11)
        self.assertEqual(normalized["url"], "https://example.test/pages/incident-guide")
        self.assertEqual(normalized["created_at"], "2026-06-18T00:00:00Z")
        self.assertEqual(normalized["updated_at"], "2026-06-18T01:00:00Z")
        self.assertIs(normalized["raw"], raw)


class ListPagesClientTestCase(unittest.TestCase):
    def test_list_pages_passes_optional_params_when_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.list_pages(count=25, offset=50)

        request.assert_called_once_with("GET", "pages", params={"count": 25, "offset": 50})
        self.assertEqual(result, {"data": [], "total": 0})

    def test_list_pages_omits_optional_params_when_not_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            result = client.list_pages()

        request.assert_called_once_with("GET", "pages")
        self.assertEqual(result, {"data": []})

    def test_list_pages_rejects_invalid_response_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": "not-a-list"}):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client.list_pages()


if __name__ == "__main__":
    unittest.main()
