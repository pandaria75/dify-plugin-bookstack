from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, InvalidResponseError
from tools.list_books import ListBooksTool, normalize_book_result


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
            result = client.list_books(count=25, offset=50, sort="+name", filters='{"name:eq":"Operations"}')

        request.assert_called_once_with(
            "GET",
            "books",
            params={"count": 25, "offset": 50, "sort": "name", "filter[name:eq]": "Operations"},
        )
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


class ListBooksToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ListBooksTool)
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

    @patch("tools.list_books.BookStackClient.from_credentials")
    def test_forwards_sort_filters_and_pagination(self, from_credentials: Mock) -> None:
        client = Mock()
        client.list_books.return_value = {"data": [{"id": 7, "name": "Operations"}], "total": 1}
        from_credentials.return_value = client

        result = self._invoke(count=25, offset=50, sort="-updated_at", filters='{"name:like":"%Ops%"}')

        client.list_books.assert_called_once_with(
            count=25,
            offset=50,
            sort="-updated_at",
            filters='{"name:like":"%Ops%"}',
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["books"][0]["book_id"], 7)


class ListBooksYamlContractTestCase(unittest.TestCase):
    def test_yaml_keeps_existing_params_and_adds_sort_and_filters(self):
        content = Path("tools/list_books.yaml").read_text(encoding="utf-8")

        for required_snippet in ("- name: count", "- name: offset", "- name: sort", "- name: filters"):
            with self.subTest(snippet=required_snippet):
                self.assertIn(required_snippet, content)


if __name__ == "__main__":
    unittest.main()
