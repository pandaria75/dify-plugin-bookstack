from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookStackClient, InvalidResponseError
from tools.list_shelves import normalize_shelf_result


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
            result = client.list_shelves(count=25, offset=50)

        request.assert_called_once_with("GET", "shelves", params={"count": 25, "offset": 50})
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


if __name__ == "__main__":
    unittest.main()
