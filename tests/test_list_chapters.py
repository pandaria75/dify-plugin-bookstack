from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookNotFoundError, BookStackClient, InvalidResponseError
from tools.list_chapters import normalize_chapter_result


class ListChaptersMappingTestCase(unittest.TestCase):
    def test_normalize_chapter_result_preserves_supported_fields(self):
        raw = {
            "id": 11,
            "name": "Runbooks",
            "slug": "runbooks",
            "book_id": 7,
            "description": "Operations runbooks",
            "url": "https://example.test/chapters/runbooks",
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "extra": "keep-in-raw",
        }

        normalized = normalize_chapter_result(raw)

        self.assertEqual(normalized["chapter_id"], 11)
        self.assertEqual(normalized["name"], "Runbooks")
        self.assertEqual(normalized["slug"], "runbooks")
        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["description"], "Operations runbooks")
        self.assertEqual(normalized["url"], "https://example.test/chapters/runbooks")
        self.assertEqual(normalized["created_at"], "2026-06-18T00:00:00Z")
        self.assertEqual(normalized["updated_at"], "2026-06-18T01:00:00Z")
        self.assertIs(normalized["raw"], raw)


class ListChaptersClientTestCase(unittest.TestCase):
    def test_list_chapters_passes_filter_and_pagination_when_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.list_chapters(book_id=7, count=25, offset=50)

        request.assert_called_once_with(
            "GET",
            "chapters",
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
            params={"book_id": 7, "count": 25, "offset": 50},
        )
        self.assertEqual(result, {"data": [], "total": 0})

    def test_list_chapters_omits_optional_params_when_not_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            result = client.list_chapters()

        request.assert_called_once_with(
            "GET",
            "chapters",
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )
        self.assertEqual(result, {"data": []})

    def test_list_chapters_rejects_invalid_response_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": "not-a-list"}):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client.list_chapters()


if __name__ == "__main__":
    unittest.main()
