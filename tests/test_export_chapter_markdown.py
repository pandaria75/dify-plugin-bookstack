from __future__ import annotations

import unittest
from unittest.mock import Mock, call, patch

from bookstack_client import ChapterNotFoundError, ServiceUnavailableError
from tools.export_chapter_markdown import ExportChapterMarkdownTool


class ExportChapterMarkdownToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ExportChapterMarkdownTool)
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

    @patch("tools.export_chapter_markdown.BookStackClient.from_credentials")
    def test_requires_chapter_id(self, from_credentials: Mock) -> None:
        result = self._invoke(chapter_id="   ")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "chapter_id is required",
                "chapter_id": None,
                "title": None,
                "url": None,
                "markdown": None,
                "content_format": None,
                "book_id": None,
                "pages": None,
                "raw": None,
            },
        )

    @patch("tools.export_chapter_markdown.BookStackClient.from_credentials")
    def test_exports_aggregate_markdown_and_preserves_chapter_page_order(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_chapter.return_value = {
            "id": 11,
            "name": "Deploy",
            "url": "https://example.test/chapters/11",
            "book_id": 7,
            "pages": [{"id": 22}, {"id": 21}],
        }
        client.export_chapter_markdown.return_value = "# Deploy\n\nAll pages"
        client.get_page.side_effect = [
            {"id": 22, "name": "Second", "markdown": "## Second"},
            {"id": 21, "name": "First", "markdown": "## First"},
        ]
        from_credentials.return_value = client

        result = self._invoke(chapter_id=" 11 ")

        client.get_chapter.assert_called_once_with("11")
        client.export_chapter_markdown.assert_called_once_with("11")
        self.assertEqual(client.get_page.call_args_list, [call("22"), call("21")])
        self.assertEqual(result["success"], True)
        self.assertIsNone(result["error"])
        self.assertEqual(result["chapter_id"], 11)
        self.assertEqual(result["title"], "Deploy")
        self.assertEqual(result["book_id"], 7)
        self.assertEqual(result["markdown"], "# Deploy\n\nAll pages")
        self.assertEqual([page["page_id"] for page in result["pages"]], [22, 21])
        self.assertEqual([page["title"] for page in result["pages"]], ["Second", "First"])

    @patch("tools.export_chapter_markdown.BookStackClient.from_credentials")
    def test_preserves_chapter_not_found_error_term(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_chapter.side_effect = ChapterNotFoundError("Chapter not found")
        from_credentials.return_value = client

        result = self._invoke(chapter_id="11")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "Chapter not found")
        self.assertIsNone(result["markdown"])
        self.assertIsNone(result["pages"])

    @patch("tools.export_chapter_markdown.BookStackClient.from_credentials")
    def test_preserves_service_unavailable_error_term(self, from_credentials: Mock) -> None:
        client = Mock()
        client.export_chapter_markdown.side_effect = ServiceUnavailableError("BookStack API unavailable")
        client.get_chapter.return_value = {"id": 11, "pages": []}
        from_credentials.return_value = client

        result = self._invoke(chapter_id="11")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "BookStack API unavailable")
        self.assertIsNone(result["markdown"])
        self.assertIsNone(result["pages"])

    @patch("tools.export_chapter_markdown.BookStackClient.from_credentials")
    def test_allows_empty_chapter_pages_list(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_chapter.return_value = {"id": 11, "name": "Deploy", "pages": []}
        client.export_chapter_markdown.return_value = "# Deploy"
        from_credentials.return_value = client

        result = self._invoke(chapter_id="11")

        client.get_page.assert_not_called()
        self.assertEqual(result["success"], True)
        self.assertEqual(result["markdown"], "# Deploy")
        self.assertEqual(result["pages"], [])

    @patch("tools.export_chapter_markdown.BookStackClient.from_credentials")
    def test_rejects_missing_or_non_list_pages(self, from_credentials: Mock) -> None:
        for raw_chapter in ({"id": 11}, {"id": 11, "pages": "nope"}):
            with self.subTest(raw_chapter=raw_chapter):
                client = Mock()
                client.get_chapter.return_value = raw_chapter
                client.export_chapter_markdown.return_value = "# Deploy"
                from_credentials.return_value = client

                result = self._invoke(chapter_id="11")

                self.assertEqual(result["success"], False)
                self.assertEqual(result["error"], "Invalid BookStack response")
                self.assertIsNone(result["pages"])


if __name__ == "__main__":
    unittest.main()
