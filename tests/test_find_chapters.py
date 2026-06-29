from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from tools.find_chapters import FindChaptersTool
from tools.find_books import normalize_find_match


class FindChaptersToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(FindChaptersTool)
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

    @patch("tools.find_chapters.BookStackClient.from_credentials")
    def test_requires_name(self, from_credentials: Mock) -> None:
        result = self._invoke(name="   ", match="like")

        from_credentials.assert_not_called()
        self.assertEqual(result, {"success": False, "error": "name is required", "chapters": [], "count": 0, "total": None})

    @patch("tools.find_chapters.BookStackClient.from_credentials")
    def test_forwards_match_scope_and_maps_results(self, from_credentials: Mock) -> None:
        client = Mock()
        client.find_chapters.return_value = {
            "data": [
                {
                    "id": 11,
                    "name": "Runbooks",
                    "slug": "runbooks",
                    "book_id": 7,
                    "description": "Ops chapters",
                    "url": "https://example.test/chapters/runbooks",
                }
            ],
            "total": 2,
        }
        from_credentials.return_value = client

        result = self._invoke(name=" Runbooks ", match=" Exact ", book_id="7", count=5, offset=10)

        client.find_chapters.assert_called_once_with("Runbooks", match="exact", book_id="7", count=5, offset=10)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["chapters"][0]["chapter_id"], 11)

    @patch("tools.find_chapters.BookStackClient.from_credentials")
    def test_rejects_unsupported_match_before_client_call(self, from_credentials: Mock) -> None:
        result = self._invoke(name="Runbooks", match="prefix")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "match must be one of: exact, like",
                "chapters": [],
                "count": 0,
                "total": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
