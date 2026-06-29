from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import PageNotFoundError, ServiceUnavailableError
from tools.export_page_markdown import ExportPageMarkdownTool, normalize_export_page_markdown_result


class ExportPageMarkdownNormalizationTestCase(unittest.TestCase):
    def test_normalize_export_page_markdown_result_prefers_markdown(self):
        raw = {
            "id": 42,
            "name": "Runbook",
            "url": "https://example.test/pages/42",
            "markdown": "# Runbook",
            "body": "Legacy body",
            "book_id": 7,
            "chapter_id": 11,
            "slug": "runbook",
        }

        normalized = normalize_export_page_markdown_result(raw)

        self.assertEqual(normalized["page_id"], 42)
        self.assertEqual(normalized["title"], "Runbook")
        self.assertEqual(normalized["markdown"], "# Runbook")
        self.assertEqual(normalized["content_format"], "markdown")
        self.assertIs(normalized["raw"], raw)

    def test_normalize_export_page_markdown_result_falls_back_to_body_and_title(self):
        raw = {"id": 99, "title": "Fallback Title", "body": "Legacy body"}

        normalized = normalize_export_page_markdown_result(raw)

        self.assertEqual(normalized["title"], "Fallback Title")
        self.assertEqual(normalized["markdown"], "Legacy body")


class ExportPageMarkdownToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ExportPageMarkdownTool)
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

    @patch("tools.export_page_markdown.BookStackClient.from_credentials")
    def test_requires_page_id(self, from_credentials: Mock) -> None:
        result = self._invoke(page_id="   ")

        from_credentials.assert_not_called()
        self.assertEqual(
            result,
            {
                "success": False,
                "error": "page_id is required",
                "page_id": None,
                "title": None,
                "url": None,
                "markdown": None,
                "content_format": None,
                "book_id": None,
                "chapter_id": None,
                "slug": None,
                "raw": None,
            },
        )

    @patch("tools.export_page_markdown.BookStackClient.from_credentials")
    def test_exports_markdown_by_page_id(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_page.return_value = {
            "id": 42,
            "name": "Runbook",
            "url": "https://example.test/pages/42",
            "markdown": "# Runbook",
            "book_id": 7,
            "chapter_id": 11,
            "slug": "runbook",
        }
        from_credentials.return_value = client

        result = self._invoke(page_id=" 42 ")

        client.get_page.assert_called_once_with("42")
        self.assertEqual(result["success"], True)
        self.assertEqual(result["error"], None)
        self.assertEqual(result["page_id"], 42)
        self.assertEqual(result["markdown"], "# Runbook")
        self.assertEqual(result["content_format"], "markdown")

    @patch("tools.export_page_markdown.BookStackClient.from_credentials")
    def test_preserves_page_not_found_error_term(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_page.side_effect = PageNotFoundError("Page not found")
        from_credentials.return_value = client

        result = self._invoke(page_id="42")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "Page not found")
        self.assertIsNone(result["markdown"])

    @patch("tools.export_page_markdown.BookStackClient.from_credentials")
    def test_preserves_service_unavailable_error_term(self, from_credentials: Mock) -> None:
        client = Mock()
        client.get_page.side_effect = ServiceUnavailableError("BookStack API unavailable")
        from_credentials.return_value = client

        result = self._invoke(page_id="42")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "BookStack API unavailable")
        self.assertIsNone(result["markdown"])


if __name__ == "__main__":
    unittest.main()
