from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, BookNotFoundError
from tools.get_book import GetBookTool, normalize_book_result


class GetBookMappingTestCase(unittest.TestCase):
    def test_normalize_book_result_returns_expected_fields_and_raw(self):
        raw = {
            "id": 7,
            "name": "Operations",
            "slug": "operations",
            "description": "Ops docs",
            "description_html": "<p>Ops docs</p>",
            "url": "https://example.test/books/operations",
            "tags": [{"name": "team", "value": "ops"}],
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "created_by": {"id": 2, "name": "Alice"},
            "updated_by": {"id": 3, "name": "Bob"},
        }

        normalized = normalize_book_result(raw)

        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["name"], "Operations")
        self.assertEqual(normalized["slug"], "operations")
        self.assertEqual(normalized["description_html"], "<p>Ops docs</p>")
        self.assertEqual(normalized["tags"], [{"name": "team", "value": "ops"}])
        self.assertIs(normalized["raw"], raw)


class GetBookClientTestCase(unittest.TestCase):
    def test_get_book_uses_book_not_found_mapping(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 7}) as request:
            result = client.get_book(7)

        request.assert_called_once_with(
            "GET",
            "books/7",
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )
        self.assertEqual(result, {"id": 7})


class GetBookToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(GetBookTool)
        self.tool.runtime = Mock()
        self.tool.runtime.credentials = {"base_url": "https://example.com", "token_id": "id", "token_secret": "secret"}
        self.tool.create_variable_message = Mock(
            side_effect=lambda variable_name, variable_value: {
                "variable_name": variable_name,
                "variable_value": variable_value,
            }
        )

    def _invoke(self, **params):
        return {message["variable_name"]: message["variable_value"] for message in self.tool._invoke(params)}

    @patch("tools.get_book.BookStackClient.from_credentials")
    def test_requires_book_id(self, from_credentials: Mock) -> None:
        result = self._invoke(book_id="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "book_id is required")

    @patch("tools.get_book.BookStackClient.from_credentials")
    def test_reads_book_and_returns_normalized_payload(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_book.return_value = {"id": 7, "name": "Operations", "slug": "operations"}
        from_credentials.return_value = client

        result = self._invoke(book_id=" 7 ")

        client.get_book.assert_called_once_with("7")
        self.assertEqual(result["success"], True)
        self.assertEqual(result["book_id"], 7)
        self.assertEqual(result["name"], "Operations")


if __name__ == "__main__":
    unittest.main()
