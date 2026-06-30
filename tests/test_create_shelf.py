from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient
from tools.create_shelf import CreateShelfTool, normalize_created_shelf_result


class CreateShelfMappingTestCase(unittest.TestCase):
    def test_normalize_created_shelf_result_adds_action_and_raw(self):
        raw = {
            "id": 13,
            "name": "Publishing",
            "slug": "publishing",
            "url": "https://example.test/shelves/publishing",
        }

        normalized = normalize_created_shelf_result(raw)

        self.assertEqual(normalized["shelf_id"], 13)
        self.assertEqual(normalized["name"], "Publishing")
        self.assertEqual(normalized["action"], "created")
        self.assertIs(normalized["raw"], raw)


class CreateShelfClientTestCase(unittest.TestCase):
    def test_create_shelf_sends_normalized_resource_payload(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 13}) as request:
            result = client.create_shelf(
                name="Publishing",
                description="Shelf docs",
                description_html="<p>Shelf docs</p>",
                books=[1, 2],
                tags=[{"name": "team", "value": "ops"}],
            )

        request.assert_called_once_with(
            "POST",
            "shelves",
            json={
                "name": "Publishing",
                "description": "Shelf docs",
                "description_html": "<p>Shelf docs</p>",
                "books": [1, 2],
                "tags": [{"name": "team", "value": "ops"}],
            },
        )
        self.assertEqual(result, {"id": 13})


class CreateShelfToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(CreateShelfTool)
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

    @patch("tools.create_shelf.BookStackClient.from_credentials")
    def test_requires_name(self, from_credentials: Mock) -> None:
        result = self._invoke(name="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "name is required")

    @patch("tools.create_shelf.BookStackClient.from_credentials")
    def test_normalizes_optional_fields_books_and_tags(self, from_credentials: Mock) -> None:
        client = Mock()
        client.create_shelf.return_value = {"id": 13, "name": "Publishing", "slug": "publishing"}
        from_credentials.return_value = client

        result = self._invoke(
            name=" Publishing ",
            description=" Shelf docs ",
            description_html=" <p>Shelf docs</p> ",
            books=[" 7 ", "8"],
            tags=["team:ops", "status:active"],
        )

        client.create_shelf.assert_called_once_with(
            name="Publishing",
            description="Shelf docs",
            description_html="<p>Shelf docs</p>",
            books=[7, 8],
            tags=[
                {"name": "team", "value": "ops"},
                {"name": "status", "value": "active"},
            ],
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "created")

    @patch("tools.create_shelf.BookStackClient.from_credentials")
    def test_rejects_non_integer_book_ids(self, from_credentials: Mock) -> None:
        result = self._invoke(name="Publishing", books=["x"])

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "books entries must be integers")


if __name__ == "__main__":
    unittest.main()
