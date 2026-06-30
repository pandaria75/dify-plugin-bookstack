from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient
from tools.create_book import CreateBookTool, normalize_created_book_result


class CreateBookMappingTestCase(unittest.TestCase):
    def test_normalize_created_book_result_adds_action_and_raw(self):
        raw = {
            "id": 7,
            "name": "Operations",
            "slug": "operations",
            "url": "https://example.test/books/operations",
        }

        normalized = normalize_created_book_result(raw)

        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["name"], "Operations")
        self.assertEqual(normalized["action"], "created")
        self.assertIs(normalized["raw"], raw)


class CreateBookClientTestCase(unittest.TestCase):
    def test_create_book_sends_normalized_resource_payload(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 7}) as request:
            result = client.create_book(
                name="Operations",
                description="Ops docs",
                description_html="<p>Ops docs</p>",
                tags=[{"name": "team", "value": "ops"}],
            )

        request.assert_called_once_with(
            "POST",
            "books",
            json={
                "name": "Operations",
                "description": "Ops docs",
                "description_html": "<p>Ops docs</p>",
                "tags": [{"name": "team", "value": "ops"}],
            },
        )
        self.assertEqual(result, {"id": 7})


class CreateBookToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(CreateBookTool)
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

    @patch("tools.create_book.BookStackClient.from_credentials")
    def test_requires_name(self, from_credentials: Mock) -> None:
        result = self._invoke(name="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "name is required")

    @patch("tools.create_book.BookStackClient.from_credentials")
    def test_normalizes_optional_fields_and_tags(self, from_credentials: Mock) -> None:
        client = Mock()
        client.create_book.return_value = {"id": 7, "name": "Operations", "slug": "operations"}
        from_credentials.return_value = client

        result = self._invoke(
            name=" Operations ",
            description=" Ops docs ",
            description_html=" <p>Ops docs</p> ",
            tags=["team:ops", "status:active"],
        )

        client.create_book.assert_called_once_with(
            name="Operations",
            description="Ops docs",
            description_html="<p>Ops docs</p>",
            tags=[
                {"name": "team", "value": "ops"},
                {"name": "status", "value": "active"},
            ],
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "created")


if __name__ == "__main__":
    unittest.main()
