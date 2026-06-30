from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, ChapterNotFoundError
from tools.get_chapter import GetChapterTool, normalize_chapter_result


class GetChapterMappingTestCase(unittest.TestCase):
    def test_normalize_chapter_result_returns_expected_fields_and_raw(self):
        raw = {
            "id": 11,
            "name": "Runbooks",
            "slug": "runbooks",
            "book_id": 7,
            "description": "Ops docs",
            "description_html": "<p>Ops docs</p>",
            "priority": 3,
            "url": "https://example.test/chapters/runbooks",
            "tags": [{"name": "team", "value": "ops"}],
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "created_by": {"id": 2, "name": "Alice"},
            "updated_by": {"id": 3, "name": "Bob"},
        }

        normalized = normalize_chapter_result(raw)

        self.assertEqual(normalized["chapter_id"], 11)
        self.assertEqual(normalized["description_html"], "<p>Ops docs</p>")
        self.assertEqual(normalized["priority"], 3)
        self.assertEqual(normalized["tags"], [{"name": "team", "value": "ops"}])
        self.assertIs(normalized["raw"], raw)


class GetChapterClientTestCase(unittest.TestCase):
    def test_get_chapter_uses_chapter_not_found_mapping(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 11}) as request:
            result = client.get_chapter(11)

        request.assert_called_once_with(
            "GET",
            "chapters/11",
            not_found_error=ChapterNotFoundError,
            not_found_message="Chapter not found",
        )
        self.assertEqual(result, {"id": 11})


class GetChapterToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(GetChapterTool)
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

    @patch("tools.get_chapter.BookStackClient.from_credentials")
    def test_requires_chapter_id(self, from_credentials: Mock) -> None:
        result = self._invoke(chapter_id="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "chapter_id is required")

    @patch("tools.get_chapter.BookStackClient.from_credentials")
    def test_reads_chapter_and_returns_normalized_payload(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_chapter.return_value = {"id": 11, "name": "Runbooks", "slug": "runbooks", "book_id": 7}
        from_credentials.return_value = client

        result = self._invoke(chapter_id=" 11 ")

        client.get_chapter.assert_called_once_with("11")
        self.assertEqual(result["success"], True)
        self.assertEqual(result["chapter_id"], 11)
        self.assertEqual(result["name"], "Runbooks")


if __name__ == "__main__":
    unittest.main()
