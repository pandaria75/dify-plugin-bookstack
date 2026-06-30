from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, ShelfNotFoundError
from tools.update_shelf import UpdateShelfTool, normalize_updated_shelf_result


class UpdateShelfMappingTestCase(unittest.TestCase):
    def test_normalize_updated_shelf_result_adds_action_and_raw(self):
        raw = {
            "id": 13,
            "name": "Publishing",
            "slug": "publishing",
            "url": "https://example.test/shelves/publishing",
        }

        normalized = normalize_updated_shelf_result(raw)

        self.assertEqual(normalized["shelf_id"], 13)
        self.assertEqual(normalized["action"], "updated")
        self.assertIs(normalized["raw"], raw)


class UpdateShelfClientTestCase(unittest.TestCase):
    def test_update_shelf_sends_normalized_resource_payload(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 13}) as request:
            result = client.update_shelf(
                "13",
                name="Publishing",
                description="Shelf docs",
                description_html="<p>Shelf docs</p>",
                books=[1, 2],
                tags=[{"name": "team", "value": "ops"}],
            )

        request.assert_called_once_with(
            "PUT",
            "shelves/13",
            json={
                "name": "Publishing",
                "description": "Shelf docs",
                "description_html": "<p>Shelf docs</p>",
                "books": [1, 2],
                "tags": [{"name": "team", "value": "ops"}],
            },
            not_found_error=ShelfNotFoundError,
            not_found_message="Shelf not found",
        )
        self.assertEqual(result, {"id": 13})


class UpdateShelfToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(UpdateShelfTool)
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

    @patch("tools.update_shelf.BookStackClient.from_credentials")
    def test_requires_shelf_id(self, from_credentials: Mock) -> None:
        result = self._invoke(shelf_id="   ", name="Publishing")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "shelf_id is required")

    @patch("tools.update_shelf.BookStackClient.from_credentials")
    def test_requires_at_least_one_non_empty_update_field(self, from_credentials: Mock) -> None:
        result = self._invoke(shelf_id="13", description="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "at least one update field is required")

    @patch("tools.update_shelf.BookStackClient.from_credentials")
    def test_normalizes_and_forwards_updates(self, from_credentials: Mock) -> None:
        client = Mock()
        client.update_shelf.return_value = {"id": 13, "name": "Publishing", "slug": "publishing"}
        from_credentials.return_value = client

        result = self._invoke(
            shelf_id=" 13 ",
            name=" Publishing ",
            description=" Shelf docs ",
            description_html=" <p>Shelf docs</p> ",
            books=[" 7 ", "8"],
            tags="team:ops",
        )

        client.update_shelf.assert_called_once_with(
            "13",
            name="Publishing",
            description="Shelf docs",
            description_html="<p>Shelf docs</p>",
            books=[7, 8],
            tags=[{"name": "team", "value": "ops"}],
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "updated")

    @patch("tools.update_shelf.BookStackClient.from_credentials")
    def test_rejects_non_integer_book_ids(self, from_credentials: Mock) -> None:
        result = self._invoke(shelf_id="13", books=["x"])

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "books entries must be integers")


if __name__ == "__main__":
    unittest.main()
