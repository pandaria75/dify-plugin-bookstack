from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient
from tools.list_tag_names import ListTagNamesTool, normalize_tag_name_result


class ListTagNamesMappingTestCase(unittest.TestCase):
    def test_normalize_tag_name_result_supports_dict_items(self):
        raw = {"name": "doc_id", "count": 3}

        normalized = normalize_tag_name_result(raw)

        self.assertEqual(normalized["name"], "doc_id")
        self.assertIs(normalized["raw"], raw)

    def test_normalize_tag_name_result_supports_scalar_items(self):
        normalized = normalize_tag_name_result("doc_id")

        self.assertEqual(normalized, {"name": "doc_id", "raw": "doc_id"})


class ListTagNamesClientTestCase(unittest.TestCase):
    def test_list_tag_names_uses_client_method(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.list_tag_names(count=25, offset=50)

        request.assert_called_once_with("GET", "tags/names", params={"count": 25, "offset": 50})
        self.assertEqual(result, {"data": [], "total": 0})


class ListTagNamesToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ListTagNamesTool)
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

    @patch("tools.list_tag_names.BookStackClient.from_credentials")
    def test_lists_tag_names_and_returns_simple_payload(self, from_credentials: Mock) -> None:
        client = Mock()
        client.list_tag_names.return_value = {"data": ["doc_id", {"name": "env"}], "total": 8}
        from_credentials.return_value = client

        result = self._invoke(count=2, offset=4)

        client.list_tag_names.assert_called_once_with(count=2, offset=4)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["total"], 8)
        self.assertEqual(result["tag_names"][0], {"name": "doc_id", "raw": "doc_id"})
        self.assertEqual(result["tag_names"][1]["name"], "env")


if __name__ == "__main__":
    unittest.main()
