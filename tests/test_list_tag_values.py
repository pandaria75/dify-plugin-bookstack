from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient
from tools.list_tag_values import ListTagValuesTool, normalize_tag_value_result


class ListTagValuesMappingTestCase(unittest.TestCase):
    def test_normalize_tag_value_result_supports_dict_items(self):
        raw = {"name": "doc_id", "value": "123"}

        normalized = normalize_tag_value_result(raw, name="fallback")

        self.assertEqual(normalized["name"], "doc_id")
        self.assertEqual(normalized["value"], "123")
        self.assertIs(normalized["raw"], raw)

    def test_normalize_tag_value_result_supports_scalar_items(self):
        normalized = normalize_tag_value_result("123", name="doc_id")

        self.assertEqual(normalized, {"name": "doc_id", "value": "123", "raw": "123"})


class ListTagValuesClientTestCase(unittest.TestCase):
    def test_list_tag_values_uses_client_method(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.list_tag_values("doc_id", count=25, offset=50)

        request.assert_called_once_with(
            "GET",
            "tags/values-for-name",
            params={"name": "doc_id", "count": 25, "offset": 50},
        )
        self.assertEqual(result, {"data": [], "total": 0})


class ListTagValuesToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ListTagValuesTool)
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

    @patch("tools.list_tag_values.BookStackClient.from_credentials")
    def test_requires_name(self, from_credentials: Mock) -> None:
        result = self._invoke(name="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "name is required")

    @patch("tools.list_tag_values.BookStackClient.from_credentials")
    def test_lists_tag_values_and_returns_simple_payload(self, from_credentials: Mock) -> None:
        client = Mock()
        client.list_tag_values.return_value = {"data": ["123", {"value": "456"}], "total": 9}
        from_credentials.return_value = client

        result = self._invoke(name=" doc_id ", count=2, offset=4)

        client.list_tag_values.assert_called_once_with("doc_id", count=2, offset=4)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["total"], 9)
        self.assertEqual(result["tag_values"][0], {"name": "doc_id", "value": "123", "raw": "123"})
        self.assertEqual(result["tag_values"][1]["name"], "doc_id")
        self.assertEqual(result["tag_values"][1]["value"], "456")


if __name__ == "__main__":
    unittest.main()
