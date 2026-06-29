from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from tools.find_shelves import FindShelvesTool, normalize_find_match


class FindShelvesNormalizationTestCase(unittest.TestCase):
    def test_normalize_find_match_accepts_supported_values(self):
        self.assertEqual(normalize_find_match(" Exact "), "exact")
        self.assertEqual(normalize_find_match("LIKE"), "like")

    def test_normalize_find_match_rejects_unsupported_values(self):
        with self.assertRaisesRegex(ValueError, "match must be one of: exact, like"):
            normalize_find_match("prefix")


class FindShelvesToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(FindShelvesTool)
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

    @patch("tools.find_shelves.BookStackClient.from_credentials")
    def test_requires_name(self, from_credentials: Mock) -> None:
        result = self._invoke(name="   ", match="like")

        from_credentials.assert_not_called()
        self.assertEqual(result, {"success": False, "error": "name is required", "shelves": [], "count": 0, "total": None})

    @patch("tools.find_shelves.BookStackClient.from_credentials")
    def test_forwards_match_and_maps_results(self, from_credentials: Mock) -> None:
        client = Mock()
        client.find_shelves.return_value = {
            "data": [
                {
                    "id": 11,
                    "name": "Engineering",
                    "slug": "engineering",
                    "description": "Team shelf",
                    "url": "https://example.test/shelves/engineering",
                }
            ],
            "total": 4,
        }
        from_credentials.return_value = client

        result = self._invoke(name=" Engineering ", match=" LIKE ", count=5, offset=10)

        client.find_shelves.assert_called_once_with("Engineering", match="like", count=5, offset=10)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["shelves"][0]["shelf_id"], 11)

    @patch("tools.find_shelves.BookStackClient.from_credentials")
    def test_rejects_unsupported_match_before_client_call(self, from_credentials: Mock) -> None:
        result = self._invoke(name="Engineering", match="prefix")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "match must be one of: exact, like",
                "shelves": [],
                "count": 0,
                "total": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
