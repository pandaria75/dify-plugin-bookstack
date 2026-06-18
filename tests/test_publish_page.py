from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackError
from tools.publish_page import PublishPageTool


class PublishPageToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = PublishPageTool()
        self.tool.runtime = Mock()
        self.tool.runtime.credentials = {"base_url": "https://example.com", "token_id": "id", "token_secret": "secret"}
        self.tool.create_json_message = Mock(side_effect=lambda payload: payload)
        self.tool.create_text_message = Mock(side_effect=lambda text: text)

    def _invoke(self, **params):
        return list(self.tool._invoke(params))[0]

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_updates_by_page_id(self, from_credentials: Mock) -> None:
        client = Mock()
        client.update_page.return_value = {"id": 7, "name": "Title", "url": "/pages/7"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", page_id="7")

        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "updated")
        client.update_page.assert_called_once_with("7", title="Title", markdown="Body", tags=None, book_id=None, chapter_id=None)
        client.search_pages.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_exact_title_match_updates(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = [{"id": 9, "name": "  Title  ", "url": "/pages/9"}]
        client.update_page.return_value = {"id": 9, "name": "Title", "url": "/pages/9"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body")

        self.assertEqual(result["action"], "updated")
        client.update_page.assert_called_once_with(9, title="Title", markdown="Body", tags=None, book_id=None, chapter_id=None)

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_fuzzy_non_exact_single_result_rejected(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = [{"id": 9, "name": "Title - draft", "url": "/pages/9"}]
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body")

        self.assertEqual(result, "success=false\nerror=book_id or chapter_id is required to create a new page")
        client.update_page.assert_not_called()
        client.create_page.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_fuzzy_non_exact_with_location_creates(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = [{"id": 9, "name": "Title - draft", "url": "/pages/9"}]
        client.create_page.return_value = {"id": 5, "name": "Title", "url": "/pages/5"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", book_id="8")

        self.assertEqual(result["action"], "created")
        client.update_page.assert_not_called()
        client.create_page.assert_called_once_with(title="Title", markdown="Body", tags=None, book_id="8", chapter_id=None)

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_scoped_exact_match_updates_when_metadata_matches(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = [
            {"id": 1, "name": "Title", "url": "/pages/1", "book_id": 8},
            {"id": 2, "name": "Title", "url": "/pages/2", "book_id": 9},
        ]
        client.update_page.return_value = {"id": 1, "name": "Title", "url": "/pages/1"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", book_id="8")

        self.assertEqual(result["action"], "updated")
        client.update_page.assert_called_once_with(1, title="Title", markdown="Body", tags=None, book_id="8", chapter_id=None)

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_creates_when_no_match_and_location_provided(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = []
        client.create_page.return_value = {"id": 5, "name": "Title", "url": "/pages/5"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", book_id="8")

        self.assertEqual(result["action"], "created")
        client.create_page.assert_called_once_with(title="Title", markdown="Body", tags=None, book_id="8", chapter_id=None)

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_fails_without_location_when_no_match(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = []
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body")

        self.assertEqual(result, "success=false\nerror=book_id or chapter_id is required to create a new page")
        client.create_page.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_ambiguous_matches_fail_safely(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = [
            {"id": 1, "name": "Title", "url": "/pages/1"},
            {"id": 2, "name": "Title", "url": "/pages/2"},
        ]
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body")

        self.assertEqual(result, "success=false\nerror=ambiguous title match")
        client.update_page.assert_not_called()
        client.create_page.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_client_errors_pass_through(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = BookStackError("Permission denied")
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", book_id="8")

        self.assertEqual(result, "success=false\nerror=Permission denied")


if __name__ == "__main__":
    unittest.main()
