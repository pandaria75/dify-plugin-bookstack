from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from tools.find_books import normalize_find_match
from tools.find_pages import FindPagesTool


class FindPagesToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(FindPagesTool)
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

    def test_normalize_find_match_rejects_unsupported_values(self):
        with self.assertRaisesRegex(ValueError, "match must be one of: exact, like"):
            normalize_find_match("prefix")

    @patch("tools.find_pages.BookStackClient.from_credentials")
    def test_requires_name(self, from_credentials: Mock) -> None:
        result = self._invoke(name="   ", match="like")

        from_credentials.assert_not_called()
        self.assertEqual(result, {"success": False, "error": "name is required", "pages": [], "count": 0, "total": None})

    @patch("tools.find_pages.BookStackClient.from_credentials")
    def test_forwards_match_scopes_and_maps_results(self, from_credentials: Mock) -> None:
        client = Mock()
        client.find_pages.return_value = {
            "data": [
                {
                    "id": 17,
                    "name": "On Call",
                    "slug": "on-call",
                    "book_id": 7,
                    "chapter_id": 11,
                    "url": "https://example.test/pages/on-call",
                }
            ],
            "total": 3,
        }
        from_credentials.return_value = client

        result = self._invoke(name=" On Call ", match=" LIKE ", book_id="7", chapter_id="11", count=5, offset=10)

        client.find_pages.assert_called_once_with(
            "On Call",
            match="like",
            book_id="7",
            chapter_id="11",
            count=5,
            offset=10,
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["pages"][0]["page_id"], 17)

    @patch("tools.find_pages.BookStackClient.from_credentials")
    def test_rejects_unsupported_match_before_client_call(self, from_credentials: Mock) -> None:
        result = self._invoke(name="On Call", match="prefix")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "match must be one of: exact, like",
                "pages": [],
                "count": 0,
                "total": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
