from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from tools.search_content import (
    SearchContentTool,
    normalize_search_content_result,
    normalize_search_content_types,
)


class SearchContentNormalizationTestCase(unittest.TestCase):
    def test_normalize_search_content_types_trims_lowers_aliases_and_deduplicates(self):
        self.assertEqual(
            normalize_search_content_types(" page, Shelf,book, page ,BOOKSHELF "),
            ["page", "bookshelf", "book"],
        )

    def test_normalize_search_content_types_returns_none_when_omitted(self):
        self.assertIsNone(normalize_search_content_types(None))

    def test_normalize_search_content_result_preserves_preview_and_raw(self):
        raw = {
            "id": 42,
            "type": "chapter",
            "name": "Runbooks",
            "url": "https://example.test/chapters/42",
            "preview": "Ops preview",
        }

        normalized = normalize_search_content_result(raw)

        self.assertEqual(normalized["id"], "42")
        self.assertEqual(normalized["type"], "chapter")
        self.assertEqual(normalized["title"], "Runbooks")
        self.assertEqual(normalized["preview"], "Ops preview")
        self.assertIs(normalized["raw"], raw)


class SearchContentToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(SearchContentTool)
        self.tool.runtime = Mock()
        self.tool.runtime.credentials = {"base_url": "https://example.com", "token_id": "id", "token_secret": "secret"}
        self.tool.create_variable_message = Mock(
            side_effect=lambda variable_name, variable_value: {
                "variable_name": variable_name,
                "variable_value": variable_value,
            }
        )

    def _invoke(self, **params):
        return {
            message["variable_name"]: message["variable_value"]
            for message in self.tool._invoke(params)
        }

    @patch("tools.search_content.BookStackClient.from_credentials")
    def test_requires_query(self, from_credentials: Mock) -> None:
        result = self._invoke(query="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result, {"success": False, "error": "query is required", "results": [], "count": 0, "total": None})

    @patch("tools.search_content.BookStackClient.from_credentials")
    def test_forwards_normalized_types_and_maps_results(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_content.return_value = {
            "data": [
                {
                    "id": 7,
                    "type": "bookshelf",
                    "name": "Engineering",
                    "url": "https://example.test/shelves/7",
                    "preview": "Shelf preview",
                }
            ],
            "total": 12,
        }
        from_credentials.return_value = client

        result = self._invoke(query="ops", types=" shelf, BOOKSHELF ")

        client.search_content.assert_called_once_with("ops", types=["bookshelf"])
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 12)
        self.assertEqual(result["results"][0]["type"], "bookshelf")
        self.assertEqual(result["results"][0]["preview"], "Shelf preview")

    @patch("tools.search_content.BookStackClient.from_credentials")
    def test_omits_type_filter_when_types_not_provided(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_content.return_value = {"data": []}
        from_credentials.return_value = client

        result = self._invoke(query="ops")

        client.search_content.assert_called_once_with("ops", types=None)
        self.assertEqual(result, {"success": True, "error": None, "results": [], "count": 0, "total": None})

    @patch("tools.search_content.BookStackClient.from_credentials")
    def test_rejects_unsupported_types_before_client_call(self, from_credentials: Mock) -> None:
        result = self._invoke(query="ops", types="page,unknown")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "unsupported search type: unknown",
                "results": [],
                "count": 0,
                "total": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
