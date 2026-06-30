from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, InvalidResponseError
from tools.list_pages import ListPagesTool, normalize_page_list_result


class ListPagesMappingTestCase(unittest.TestCase):
    def test_normalize_page_list_result_preserves_supported_fields(self):
        raw = {
            "id": 13,
            "name": "Incident Guide",
            "slug": "incident-guide",
            "book_id": 7,
            "chapter_id": 11,
            "url": "https://example.test/pages/incident-guide",
            "created_at": "2026-06-18T00:00:00Z",
            "updated_at": "2026-06-18T01:00:00Z",
            "extra": "keep-in-raw",
        }

        normalized = normalize_page_list_result(raw)

        self.assertEqual(normalized["page_id"], 13)
        self.assertEqual(normalized["title"], "Incident Guide")
        self.assertEqual(normalized["slug"], "incident-guide")
        self.assertEqual(normalized["book_id"], 7)
        self.assertEqual(normalized["chapter_id"], 11)
        self.assertEqual(normalized["url"], "https://example.test/pages/incident-guide")
        self.assertEqual(normalized["created_at"], "2026-06-18T00:00:00Z")
        self.assertEqual(normalized["updated_at"], "2026-06-18T01:00:00Z")
        self.assertIs(normalized["raw"], raw)


class ListPagesClientTestCase(unittest.TestCase):
    def test_list_pages_passes_optional_params_when_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.list_pages(
                book_id="7",
                chapter_id="11",
                count=25,
                offset=50,
                sort="-priority",
                filters='{"name:like":"%Guide%"}',
            )

        request.assert_called_once_with(
            "GET",
            "pages",
            params={
                "filter[book_id:eq]": "7",
                "filter[chapter_id:eq]": "11",
                "count": 25,
                "offset": 50,
                "sort": "-priority",
                "filter[name:like]": "%Guide%",
            },
        )
        self.assertEqual(result, {"data": [], "total": 0})

    def test_list_pages_omits_optional_params_when_not_provided(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            result = client.list_pages()

        request.assert_called_once_with(
            "GET",
            "pages",
        )
        self.assertEqual(result, {"data": []})

    def test_list_pages_rejects_invalid_response_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": "not-a-list"}):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client.list_pages()


class ListPagesToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(ListPagesTool)
        self.tool.runtime = Mock()
        self.tool.runtime.credentials = {"base_url": "https://example.com", "token_id": "id", "token_secret": "secret"}
        self.tool.create_variable_message = Mock(
            side_effect=lambda variable_name, variable_value: {
                "variable_name": variable_name,
                "variable_value": variable_value,
            }
        )

    def _invoke(self, **params):
        return {
            message["variable_name"]: message["variable_value"]
            for message in self.tool._invoke(params)
        }

    @patch("tools.list_pages.BookStackClient.from_credentials")
    def test_forwards_filters_and_pagination(self, from_credentials: Mock) -> None:
        client = Mock()
        client.list_pages.return_value = {"data": [{"id": 13, "name": "Incident Guide"}], "total": 1}
        from_credentials.return_value = client

        result = self._invoke(
            book_id="7",
            chapter_id="11",
            count=25,
            offset=50,
            sort="-priority",
            filters='{"name:like":"%Guide%"}',
        )

        client.list_pages.assert_called_once_with(
            book_id="7",
            chapter_id="11",
            count=25,
            offset=50,
            sort="-priority",
            filters='{"name:like":"%Guide%"}',
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["pages"][0]["page_id"], 13)

    @patch("tools.list_pages.BookStackClient.from_credentials")
    def test_preserves_no_filter_behavior(self, from_credentials: Mock) -> None:
        client = Mock()
        client.list_pages.return_value = {"data": []}
        from_credentials.return_value = client

        result = self._invoke()

        client.list_pages.assert_called_once_with(book_id=None, chapter_id=None, count=None, offset=None, sort=None, filters=None)
        self.assertEqual(result, {"success": True, "error": None, "pages": [], "count": 0, "total": None})


class ListPagesYamlContractTestCase(unittest.TestCase):
    def test_yaml_keeps_existing_params_and_adds_sort_and_filters(self):
        content = Path("tools/list_pages.yaml").read_text(encoding="utf-8")

        for required_snippet in (
            "- name: book_id",
            "- name: chapter_id",
            "- name: count",
            "- name: offset",
            "- name: sort",
            "- name: filters",
        ):
            with self.subTest(snippet=required_snippet):
                self.assertIn(required_snippet, content)


if __name__ == "__main__":
    unittest.main()
