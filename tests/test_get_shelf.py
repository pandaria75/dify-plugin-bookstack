from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, ShelfNotFoundError
from tools.get_shelf import GetShelfTool, normalize_shelf_result


class GetShelfMappingTestCase(unittest.TestCase):
    def test_normalize_shelf_result_returns_expected_fields_and_raw(self):
        raw = {
            "id": 13,
            "name": "Publishing",
            "slug": "publishing",
            "description": "Shelf docs",
            "description_html": "<p>Shelf docs</p>",
            "books": [{"id": 7, "name": "Operations"}],
            "tags": [{"name": "team", "value": "ops"}],
            "url": "https://example.test/shelves/publishing",
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "created_by": {"id": 2, "name": "Alice"},
            "updated_by": {"id": 3, "name": "Bob"},
        }

        normalized = normalize_shelf_result(raw)

        self.assertEqual(normalized["shelf_id"], 13)
        self.assertEqual(normalized["description_html"], "<p>Shelf docs</p>")
        self.assertEqual(normalized["books"], [{"id": 7, "name": "Operations"}])
        self.assertEqual(normalized["tags"], [{"name": "team", "value": "ops"}])
        self.assertIs(normalized["raw"], raw)


class GetShelfClientTestCase(unittest.TestCase):
    def test_get_shelf_uses_shelf_not_found_mapping(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 13}) as request:
            result = client.get_shelf(13)

        request.assert_called_once_with(
            "GET",
            "shelves/13",
            not_found_error=ShelfNotFoundError,
            not_found_message="Shelf not found",
        )
        self.assertEqual(result, {"id": 13})


class GetShelfToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(GetShelfTool)
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

    @patch("tools.get_shelf.BookStackClient.from_credentials")
    def test_requires_shelf_id(self, from_credentials: Mock) -> None:
        result = self._invoke(shelf_id="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "shelf_id is required")

    @patch("tools.get_shelf.BookStackClient.from_credentials")
    def test_reads_shelf_and_returns_normalized_payload(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_shelf.return_value = {"id": 13, "name": "Publishing", "slug": "publishing", "books": [{"id": 7}]}
        from_credentials.return_value = client

        result = self._invoke(shelf_id=" 13 ")

        client.get_shelf.assert_called_once_with("13")
        self.assertEqual(result["success"], True)
        self.assertEqual(result["shelf_id"], 13)
        self.assertEqual(result["name"], "Publishing")
        self.assertEqual(result["books"], [{"id": 7}])


if __name__ == "__main__":
    unittest.main()
