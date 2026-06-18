from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookStackClient, InvalidResponseError
from tools.list_books import normalize_book_result


class ListBooksMappingTestCase(unittest.TestCase):
    def test_normalize_book_result_preserves_supported_fields(self):
        raw = {
            "id": 7,
            "name": "Operations",
            "slug": "operations",
            "description": "Ops docs",
            "url": "https://example.test/books/operations",
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "extra": "keep-in-raw",
        }

        normalized = normalize_book_result(raw)

        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["name"], "Operations")
        self.assertEqual(normalized["slug"], "operations")
        self.assertEqual(normalized["description"], "Ops docs")
        self.assertEqual(normalized["url"], "https://example.test/books/operations")
        self.assertEqual(normalized["created_at"], "2026-06-18T00:00:00Z")
        self.assertEqual(normalized["updated_at"], "2026-06-18T01:00:00Z")
        self.assertIs(normalized["raw"], raw)


class ListBooksClientTestCase(unittest.TestCase):
    def test_list_books_passes_optional_params_when_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.list_books(count=25, offset=50)

        request.assert_called_once_with("GET", "books", params={"count": 25, "offset": 50})
        self.assertEqual(result, {"data": [], "total": 0})

    def test_list_books_omits_optional_params_when_not_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            result = client.list_books()

        request.assert_called_once_with("GET", "books")
        self.assertEqual(result, {"data": []})

    def test_list_books_rejects_invalid_response_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": "not-a-list"}):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client.list_books()


if __name__ == "__main__":
    unittest.main()
