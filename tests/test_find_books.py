from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from tools.find_books import FindBooksTool, normalize_find_match


class FindBooksNormalizationTestCase(unittest.TestCase):
    def test_normalize_find_match_accepts_supported_values(self):
        self.assertEqual(normalize_find_match(" Exact "), "exact")
        self.assertEqual(normalize_find_match("LIKE"), "like")

    def test_normalize_find_match_rejects_unsupported_values(self):
        with self.assertRaisesRegex(ValueError, "match must be one of: exact, like"):
            normalize_find_match("prefix")


class FindBooksToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(FindBooksTool)
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

    @patch("tools.find_books.BookStackClient.from_credentials")
    def test_requires_name(self, from_credentials: Mock) -> None:
        result = self._invoke(name="   ", match="like")

        from_credentials.assert_not_called()
        self.assertEqual(result, {"success": False, "error": "name is required", "books": [], "count": 0, "total": None})

    @patch("tools.find_books.BookStackClient.from_credentials")
    def test_forwards_match_and_maps_results(self, from_credentials: Mock) -> None:
        client = Mock()
        client.find_books.return_value = {
            "data": [
                {
                    "id": 7,
                    "name": "Operations",
                    "slug": "operations",
                    "description": "Ops docs",
                    "url": "https://example.test/books/operations",
                }
            ],
            "total": 12,
        }
        from_credentials.return_value = client

        result = self._invoke(name=" Operations ", match=" Exact ", count=5, offset=10)

        client.find_books.assert_called_once_with("Operations", match="exact", count=5, offset=10)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 12)
        self.assertEqual(result["books"][0]["book_id"], 7)

    @patch("tools.find_books.BookStackClient.from_credentials")
    def test_rejects_unsupported_match_before_client_call(self, from_credentials: Mock) -> None:
        result = self._invoke(name="Operations", match="prefix")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "match must be one of: exact, like",
                "books": [],
                "count": 0,
                "total": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
