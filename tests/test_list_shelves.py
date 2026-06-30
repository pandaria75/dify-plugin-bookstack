from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, InvalidResponseError
from tools.list_shelves import ListShelvesTool, normalize_shelf_result


class ListShelvesMappingTestCase(unittest.TestCase):
    def test_normalize_shelf_result_preserves_supported_fields(self):
        raw = {
            "id": 11,
            "name": "Engineering",
            "slug": "engineering",
            "description": "Team shelf",
            "url": "https://example.test/shelves/engineering",
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "extra": "keep-in-raw",
        }

        normalized = normalize_shelf_result(raw)

        self.assertEqual(normalized["shelf_id"], 11)
        self.assertEqual(normalized["name"], "Engineering")
        self.assertEqual(normalized["slug"], "engineering")
        self.assertEqual(normalized["description"], "Team shelf")
        self.assertEqual(normalized["url"], "https://example.test/shelves/engineering")
        self.assertEqual(normalized["created_at"], "2026-06-18T00:00:00Z")
        self.assertEqual(normalized["updated_at"], "2026-06-18T01:00:00Z")
        self.assertIs(normalized["raw"], raw)


class ListShelvesClientTestCase(unittest.TestCase):
    def test_list_shelves_passes_optional_params_when_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.list_shelves(count=25, offset=50, sort="updated_at", filters='{"name:like":"%Engineering%"}')

        request.assert_called_once_with(
            "GET",
            "shelves",
            params={"count": 25, "offset": 50, "sort": "updated_at", "filter[name:like]": "%Engineering%"},
        )
        self.assertEqual(result, {"data": [], "total": 0})

    def test_list_shelves_omits_optional_params_when_not_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            result = client.list_shelves()

        request.assert_called_once_with("GET", "shelves")
        self.assertEqual(result, {"data": []})

    def test_list_shelves_rejects_invalid_response_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": "not-a-list"}):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client.list_shelves()


class ListShelvesToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ListShelvesTool)
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

    @patch("tools.list_shelves.BookStackClient.from_credentials")
    def test_forwards_sort_filters_and_pagination(self, from_credentials: Mock) -> None:
        client = Mock()
        client.list_shelves.return_value = {"data": [{"id": 11, "name": "Engineering"}], "total": 1}
        from_credentials.return_value = client

        result = self._invoke(count=25, offset=50, sort="+updated_at", filters='{"name:like":"%Engineering%"}')

        client.list_shelves.assert_called_once_with(
            count=25,
            offset=50,
            sort="+updated_at",
            filters='{"name:like":"%Engineering%"}',
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["shelves"][0]["shelf_id"], 11)


class ListShelvesYamlContractTestCase(unittest.TestCase):
    def test_yaml_keeps_existing_params_and_adds_sort_and_filters(self):
        content = Path("tools/list_shelves.yaml").read_text(encoding="utf-8")

        for required_snippet in ("- name: count", "- name: offset", "- name: sort", "- name: filters"):
            with self.subTest(snippet=required_snippet):
                self.assertIn(required_snippet, content)


if __name__ == "__main__":
    unittest.main()
