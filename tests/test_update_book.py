from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, BookNotFoundError
from tools.update_book import UpdateBookTool, normalize_updated_book_result


class UpdateBookMappingTestCase(unittest.TestCase):
    def test_normalize_updated_book_result_adds_action_and_raw(self):
        raw = {
            "id": 7,
            "name": "Operations",
            "slug": "operations",
            "url": "https://example.test/books/operations",
        }

        normalized = normalize_updated_book_result(raw)

        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["action"], "updated")
        self.assertIs(normalized["raw"], raw)


class UpdateBookClientTestCase(unittest.TestCase):
    def test_update_book_sends_normalized_resource_payload(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 7}) as request:
            result = client.update_book(
                "7",
                name="Operations",
                description="Ops docs",
                description_html="<p>Ops docs</p>",
                tags=[{"name": "team", "value": "ops"}],
            )

        request.assert_called_once_with(
            "PUT",
            "books/7",
            json={
                "name": "Operations",
                "description": "Ops docs",
                "description_html": "<p>Ops docs</p>",
                "tags": [{"name": "team", "value": "ops"}],
            },
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )
        self.assertEqual(result, {"id": 7})


class UpdateBookToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(UpdateBookTool)
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

    @patch("tools.update_book.BookStackClient.from_credentials")
    def test_requires_book_id(self, from_credentials: Mock) -> None:
        result = self._invoke(book_id="   ", name="Operations")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "book_id is required")

    @patch("tools.update_book.BookStackClient.from_credentials")
    def test_requires_at_least_one_non_empty_update_field(self, from_credentials: Mock) -> None:
        result = self._invoke(book_id="7", description="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "at least one update field is required")

    @patch("tools.update_book.BookStackClient.from_credentials")
    def test_normalizes_and_forwards_updates(self, from_credentials: Mock) -> None:
        client = Mock()
        client.update_book.return_value = {"id": 7, "name": "Operations", "slug": "operations"}
        from_credentials.return_value = client

        result = self._invoke(
            book_id=" 7 ",
            name=" Operations ",
            description=" Ops docs ",
            description_html=" <p>Ops docs</p> ",
            tags="team:ops",
        )

        client.update_book.assert_called_once_with(
            "7",
            name="Operations",
            description="Ops docs",
            description_html="<p>Ops docs</p>",
            tags=[{"name": "team", "value": "ops"}],
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "updated")


if __name__ == "__main__":
    unittest.main()
