from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bookstack_client import BookNotFoundError, BookStackClient, InvalidResponseError
from tools.list_chapters import ListChaptersTool, normalize_chapter_result


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
            result = client.list_chapters(book_id=7, count=25, offset=50, sort="priority", filters='{"name:like":"%Run%"}')

        request.assert_called_once_with(
            "GET",
            "chapters",
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
            params={
                "filter[book_id:eq]": 7,
                "count": 25,
                "offset": 50,
                "sort": "priority",
                "filter[name:like]": "%Run%",
            },
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


class ListChaptersToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ListChaptersTool)
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

    @patch("tools.list_chapters.BookStackClient.from_credentials")
    def test_forwards_scope_sort_filters_and_pagination(self, from_credentials: Mock) -> None:
        client = Mock()
        client.list_chapters.return_value = {"data": [{"id": 11, "name": "Runbooks"}], "total": 1}
        from_credentials.return_value = client

        result = self._invoke(book_id="7", count=25, offset=50, sort="-priority", filters='{"name:eq":"Runbooks"}')

        client.list_chapters.assert_called_once_with(
            book_id="7",
            count=25,
            offset=50,
            sort="-priority",
            filters='{"name:eq":"Runbooks"}',
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["chapters"][0]["chapter_id"], 11)


class ListChaptersYamlContractTestCase(unittest.TestCase):
    def test_yaml_keeps_existing_params_and_adds_sort_and_filters(self):
        content = Path("tools/list_chapters.yaml").read_text(encoding="utf-8")

        for required_snippet in ("- name: book_id", "- name: count", "- name: offset", "- name: sort", "- name: filters"):
            with self.subTest(snippet=required_snippet):
                self.assertIn(required_snippet, content)


if __name__ == "__main__":
    unittest.main()
