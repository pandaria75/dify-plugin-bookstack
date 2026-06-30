from __future__ import annotations

import unittest
from unittest.mock import Mock, call, patch

from bookstack_client import BookNotFoundError, ServiceUnavailableError
from tools.export_book_markdown import ExportBookMarkdownTool


class ExportBookMarkdownToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ExportBookMarkdownTool)
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

    @patch("tools.export_book_markdown.BookStackClient.from_credentials")
    def test_requires_book_id(self, from_credentials: Mock) -> None:
        result = self._invoke(book_id="   ")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "book_id is required",
                "book_id": None,
                "title": None,
                "url": None,
                "markdown": None,
                "content_format": None,
                "pages": None,
                "raw": None,
            },
        )

    @patch("tools.export_book_markdown.BookStackClient.from_credentials")
    def test_exports_aggregate_markdown_and_preserves_depth_first_contents_order(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_book.return_value = {
            "id": 7,
            "name": "Operations",
            "url": "https://example.test/books/7",
            "contents": [
                {"type": "page", "id": 31},
                {"type": "chapter", "id": 11, "pages": [{"type": "page", "id": 32}, {"type": "page", "id": 33}]},
                {"type": "page", "id": 34},
            ],
        }
        client.export_book_markdown.return_value = "# Operations\n\nFull export"
        client.get_page.side_effect = [
            {"id": 31, "name": "Intro", "markdown": "# Intro"},
            {"id": 32, "name": "Deploy", "markdown": "# Deploy"},
            {"id": 33, "name": "Recover", "markdown": "# Recover"},
            {"id": 34, "name": "Appendix", "markdown": "# Appendix"},
        ]
        from_credentials.return_value = client

        result = self._invoke(book_id="7")

        client.get_book.assert_called_once_with("7")
        client.export_book_markdown.assert_called_once_with("7")
        self.assertEqual(client.get_page.call_args_list, [call("31"), call("32"), call("33"), call("34")])
        self.assertEqual(result["success"], True)
        self.assertIsNone(result["error"])
        self.assertEqual(result["book_id"], 7)
        self.assertEqual(result["title"], "Operations")
        self.assertEqual(result["markdown"], "# Operations\n\nFull export")
        self.assertEqual([page["page_id"] for page in result["pages"]], [31, 32, 33, 34])

    @patch("tools.export_book_markdown.BookStackClient.from_credentials")
    def test_preserves_book_not_found_error_term(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_book.side_effect = BookNotFoundError("Book not found")
        from_credentials.return_value = client

        result = self._invoke(book_id="7")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "Book not found")
        self.assertIsNone(result["markdown"])
        self.assertIsNone(result["pages"])

    @patch("tools.export_book_markdown.BookStackClient.from_credentials")
    def test_preserves_service_unavailable_error_term(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_book.return_value = {"id": 7, "contents": []}
        client.export_book_markdown.side_effect = ServiceUnavailableError("BookStack API unavailable")
        from_credentials.return_value = client

        result = self._invoke(book_id="7")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "BookStack API unavailable")
        self.assertIsNone(result["markdown"])
        self.assertIsNone(result["pages"])

    @patch("tools.export_book_markdown.BookStackClient.from_credentials")
    def test_allows_empty_chapter_pages_list(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_book.return_value = {
            "id": 7,
            "name": "Operations",
            "contents": [{"type": "chapter", "id": 11, "pages": []}],
        }
        client.export_book_markdown.return_value = "# Operations"
        from_credentials.return_value = client

        result = self._invoke(book_id="7")

        client.get_page.assert_not_called()
        self.assertEqual(result["success"], True)
        self.assertEqual(result["pages"], [])

    @patch("tools.export_book_markdown.BookStackClient.from_credentials")
    def test_rejects_chapter_without_pages_list(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_book.return_value = {
            "id": 7,
            "contents": [{"type": "chapter", "id": 11}],
        }
        client.export_book_markdown.return_value = "# Operations"
        from_credentials.return_value = client

        result = self._invoke(book_id="7")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "Invalid BookStack response")
        self.assertIsNone(result["pages"])

    @patch("tools.export_book_markdown.BookStackClient.from_credentials")
    def test_rejects_unknown_book_contents_type(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_book.return_value = {
            "id": 7,
            "contents": [{"type": "bookshelf", "id": 11}],
        }
        client.export_book_markdown.return_value = "# Operations"
        from_credentials.return_value = client

        result = self._invoke(book_id="7")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "Invalid BookStack response")
        self.assertIsNone(result["pages"])


if __name__ == "__main__":
    unittest.main()
