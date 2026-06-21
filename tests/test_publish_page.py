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

        result = self._invoke(title="Title", markdown="Body", page_id="7", doc_id="doc-7", path="books/title")

        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "updated")
        client.update_page.assert_called_once_with(
            "7",
            title="Title",
            markdown="Body",
            tags=[{"name": "doc_id", "value": "doc-7"}],
            book_id=None,
            chapter_id=None,
        )
        client.search_pages.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_tags_are_normalized_before_create(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.return_value = []
        client.create_page.return_value = {"id": 5, "name": "Title", "url": "/pages/5"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", book_id="8", tags=["ops", {"name": "env", "value": "prod"}])

        self.assertEqual(result["action"], "created")
        client.create_page.assert_called_once_with(
            title="Title",
            markdown="Body",
            tags=[{"name": "ops", "value": ""}, {"name": "env", "value": "prod"}],
            book_id="8",
            chapter_id=None,
        )

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
    def test_doc_id_unique_match_updates_and_passes_doc_id_tag(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [
            [
                {"id": 11, "name": "Other", "tags": [{"name": "doc_id", "value": " doc-11 "}]},
            ]
        ]
        client.update_page.return_value = {"id": 11, "name": "Title", "url": "/pages/11"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", doc_id="doc-11")

        self.assertEqual(result["action"], "updated")
        client.update_page.assert_called_once_with(
            11,
            title="Title",
            markdown="Body",
            tags=[{"name": "doc_id", "value": "doc-11"}],
            book_id=None,
            chapter_id=None,
        )

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_ambiguous_doc_id_returns_exact_error(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[
            {"id": 11, "name": "One", "tags": [{"name": "doc_id", "value": "doc-11"}]},
            {"id": 12, "name": "Two", "tags": [{"name": "doc_id", "value": "doc-11"}]},
        ]]
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", doc_id="doc-11")

        self.assertEqual(result, "success=false\nerror=ambiguous doc_id match")
        client.update_page.assert_not_called()
        client.create_page.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_path_unique_match_updates(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[
            {"id": 13, "name": "Other", "path": "books/ops/runbook"},
        ]]
        client.update_page.return_value = {"id": 13, "name": "Title", "url": "/pages/13"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", path="/books/ops/runbook/")

        self.assertEqual(result["action"], "updated")
        client.update_page.assert_called_once_with(13, title="Title", markdown="Body", tags=None, book_id=None, chapter_id=None)

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_ambiguous_path_returns_exact_error(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[
            {"id": 13, "name": "One", "path": "books/ops/runbook"},
            {"id": 14, "name": "Two", "url": "https://example.com/books/ops/runbook"},
        ]]
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", path="books/ops/runbook")

        self.assertEqual(result, "success=false\nerror=ambiguous path match")
        client.update_page.assert_not_called()
        client.create_page.assert_not_called()

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
    def test_title_fallback_still_works_after_doc_id_and_path_miss(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[], [], [{"id": 21, "name": "Title", "url": "/pages/21"}]]
        client.update_page.return_value = {"id": 21, "name": "Title", "url": "/pages/21"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", doc_id="doc-21", path="books/title")

        self.assertEqual(result["action"], "updated")
        self.assertEqual(client.search_pages.call_args_list[0].args[0], "doc-21")
        self.assertEqual(client.search_pages.call_args_list[1].args[0], "books/title")
        self.assertEqual(client.search_pages.call_args_list[2].args[0], "Title")

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_path_match_uses_cached_repeated_query_results(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[
            {"id": 22, "name": "Other", "path": "shared-query"},
        ]]
        client.update_page.return_value = {"id": 22, "name": "Title", "url": "/pages/22"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", doc_id="shared-query", path="shared-query")

        self.assertEqual(result["action"], "updated")
        client.search_pages.assert_called_once_with("shared-query")
        client.update_page.assert_called_once_with(22, title="Title", markdown="Body", tags=[{"name": "doc_id", "value": "shared-query"}], book_id=None, chapter_id=None)
        client.create_page.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_title_fallback_ambiguity_still_fails(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[], [], [
            {"id": 1, "name": "Title", "url": "/pages/1"},
            {"id": 2, "name": "Title", "url": "/pages/2"},
        ]]
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", doc_id="doc-21", path="books/title")

        self.assertEqual(result, "success=false\nerror=ambiguous title match")
        client.update_page.assert_not_called()
        client.create_page.assert_not_called()

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_no_match_with_doc_id_and_location_creates_and_includes_doc_id_tag(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[], [], []]
        client.create_page.return_value = {"id": 31, "name": "Title", "url": "/pages/31"}
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", doc_id="doc-31", path="books/title", book_id="8")

        self.assertEqual(result["action"], "created")
        client.create_page.assert_called_once_with(
            title="Title",
            markdown="Body",
            tags=[{"name": "doc_id", "value": "doc-31"}],
            book_id="8",
            chapter_id=None,
        )

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_existing_doc_id_tag_is_not_duplicated(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = [[], []]
        client.create_page.return_value = {"id": 41, "name": "Title", "url": "/pages/41"}
        from_credentials.return_value = client

        result = self._invoke(
            title="Title",
            markdown="Body",
            doc_id="doc-41",
            book_id="8",
            tags=[{"name": "doc_id", "value": "doc-41"}, {"name": "env", "value": "prod"}],
        )

        self.assertEqual(result["action"], "created")
        client.create_page.assert_called_once_with(
            title="Title",
            markdown="Body",
            tags=[{"name": "doc_id", "value": "doc-41"}, {"name": "env", "value": "prod"}],
            book_id="8",
            chapter_id=None,
        )

    @patch("tools.publish_page.BookStackClient.from_credentials")
    def test_client_errors_pass_through(self, from_credentials: Mock) -> None:
        client = Mock()
        client.search_pages.side_effect = BookStackError("Permission denied")
        from_credentials.return_value = client

        result = self._invoke(title="Title", markdown="Body", book_id="8")

        self.assertEqual(result, "success=false\nerror=Permission denied")


if __name__ == "__main__":
    unittest.main()
