from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from bookstack_client import BookStackError
from tools.create_page import CreatePageTool
from tools.get_page import GetPageTool
from tools.list_books import ListBooksTool
from tools.list_chapters import ListChaptersTool
from tools.list_pages import ListPagesTool
from tools.list_shelves import ListShelvesTool
from tools.publish_page import PublishPageTool
from tools.search_pages import SearchPagesTool
from tools.update_page import UpdatePageTool
from tools.validate_credentials import ValidateCredentialsTool


REPO_ROOT = Path(__file__).resolve().parents[1]


class ToolOutputPayloadTestCase(unittest.TestCase):
    credentials = {"base_url": "https://example.test", "token_id": "id", "token_secret": "secret"}

    def make_tool(self, tool_class: type) -> object:
        tool = object.__new__(tool_class)
        tool.runtime = Mock()
        tool.runtime.credentials = dict(self.credentials)
        tool.create_json_message = Mock(side_effect=lambda payload: payload)
        tool.create_text_message = Mock(side_effect=lambda text: text)
        tool.create_variable_message = Mock(
            side_effect=lambda variable_name, variable_value: {
                "variable_name": variable_name,
                "variable_value": variable_value,
            }
        )
        return tool

    def invoke(self, tool_class: type, params: dict[str, object]) -> dict[str, object]:
        return self.variable_messages_to_payload(self.invoke_messages(tool_class, params))

    def invoke_messages(self, tool_class: type, params: dict[str, object]) -> list[dict[str, object]]:
        tool = self.make_tool(tool_class)
        return list(tool._invoke(params))

    def variable_messages_to_payload(self, messages: list[dict[str, object]]) -> dict[str, object]:
        return {message["variable_name"]: message["variable_value"] for message in messages}

    def schema_properties(self, tool_name: str) -> dict[str, object]:
        schema_path = REPO_ROOT / "tools" / f"{tool_name}.yaml"
        with schema_path.open("r", encoding="utf-8") as file:
            tool_schema = yaml.safe_load(file)
        return tool_schema["output_schema"]["properties"]

    def nested_properties(self, tool_name: str, field_name: str) -> dict[str, object]:
        return self.schema_properties(tool_name)[field_name]["items"]["properties"]

    def assert_payload_keys_match_schema(self, payload: dict[str, object], tool_name: str) -> None:
        self.assertEqual(set(payload.keys()), set(self.schema_properties(tool_name).keys()))

    def assert_payload_keys_are_schema_subset(self, payload: dict[str, object], tool_name: str) -> None:
        self.assertTrue(set(payload.keys()).issubset(set(self.schema_properties(tool_name).keys())))

    def assert_collection_item_keys_match_schema(self, payload: dict[str, object], tool_name: str, field_name: str) -> None:
        items = payload[field_name]
        self.assertIsInstance(items, list)
        self.assertGreater(len(items), 0)
        self.assertEqual(set(items[0].keys()), set(self.nested_properties(tool_name, field_name).keys()))

    def test_validate_credentials_outputs_variable_only_success_and_error_payloads(self) -> None:
        with patch("tools.validate_credentials.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            from_credentials.return_value = client

            success_payload = self.invoke(ValidateCredentialsTool, {})

        self.assertEqual(success_payload, {"success": True, "error": None})
        self.assert_payload_keys_match_schema(success_payload, "validate_credentials")
        client.validate_credentials.assert_called_once_with()

        with patch("tools.validate_credentials.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.validate_credentials.side_effect = BookStackError("Invalid credentials")
            from_credentials.return_value = client

            error_payload = self.invoke(ValidateCredentialsTool, {})

        self.assertEqual(error_payload, {"success": False, "error": "Invalid credentials"})
        self.assert_payload_keys_match_schema(error_payload, "validate_credentials")

    def test_list_tools_output_schema_aligned_success_and_error_payloads(self) -> None:
        cases = [
            (
                "list_books",
                ListBooksTool,
                "books",
                "list_books",
                {},
                {"id": 7, "name": "Operations", "slug": "operations", "description": "Ops docs", "url": "/books/7", "created_at": "2026-06-26T00:00:00Z", "updated_at": "2026-06-26T01:00:00Z"},
            ),
            (
                "list_shelves",
                ListShelvesTool,
                "shelves",
                "list_shelves",
                {},
                {"id": 8, "name": "Engineering", "slug": "engineering", "description": "Shelf", "url": "/shelves/8", "created_at": "2026-06-26T00:00:00Z", "updated_at": "2026-06-26T01:00:00Z"},
            ),
            (
                "list_chapters",
                ListChaptersTool,
                "chapters",
                "list_chapters",
                {"book_id": "7"},
                {"id": 9, "name": "Runbooks", "slug": "runbooks", "book_id": 7, "description": "Chapter", "url": "/chapters/9", "created_at": "2026-06-26T00:00:00Z", "updated_at": "2026-06-26T01:00:00Z"},
            ),
            (
                "list_pages",
                ListPagesTool,
                "pages",
                "list_pages",
                {},
                {"id": 10, "name": "Incident Guide", "slug": "incident-guide", "book_id": 7, "chapter_id": 9, "url": "/pages/10", "created_at": "2026-06-26T00:00:00Z", "updated_at": "2026-06-26T01:00:00Z"},
            ),
        ]

        for tool_name, tool_class, field_name, client_method, params, raw_item in cases:
            with self.subTest(tool=tool_name, path="success"):
                with patch(f"tools.{tool_name}.BookStackClient.from_credentials") as from_credentials:
                    client = Mock()
                    getattr(client, client_method).return_value = {"data": [raw_item], "total": 1}
                    from_credentials.return_value = client

                    payload = self.invoke(tool_class, params)

                self.assertEqual(payload["success"], True)
                self.assertIsNone(payload["error"])
                self.assertEqual(payload["count"], 1)
                self.assertEqual(payload["total"], 1)
                self.assert_payload_keys_match_schema(payload, tool_name)
                self.assert_collection_item_keys_match_schema(payload, tool_name, field_name)

            with self.subTest(tool=tool_name, path="error"):
                with patch(f"tools.{tool_name}.BookStackClient.from_credentials") as from_credentials:
                    client = Mock()
                    getattr(client, client_method).side_effect = BookStackError("Permission denied")
                    from_credentials.return_value = client

                    payload = self.invoke(tool_class, params)

                self.assertEqual(
                    payload,
                    {"success": False, "error": "Permission denied", field_name: [], "count": 0, "total": None},
                )
                self.assert_payload_keys_match_schema(payload, tool_name)

    def test_list_books_emits_only_workflow_variable_messages(self) -> None:
        raw_book = {
            "id": 7,
            "name": "Operations",
            "slug": "operations",
            "description": "Ops docs",
            "url": "/books/7",
            "created_at": "2026-06-26T00:00:00Z",
            "updated_at": "2026-06-26T01:00:00Z",
        }

        with patch("tools.list_books.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.list_books.return_value = {"data": [raw_book], "total": 1}
            from_credentials.return_value = client

            success_messages = self.invoke_messages(ListBooksTool, {})

        self.assertEqual(
            success_messages,
            [
                {"variable_name": "success", "variable_value": True},
                {"variable_name": "error", "variable_value": None},
                {
                    "variable_name": "books",
                    "variable_value": [
                        {
                            "book_id": 7,
                            "name": "Operations",
                            "slug": "operations",
                            "description": "Ops docs",
                            "url": "/books/7",
                            "created_at": "2026-06-26T00:00:00Z",
                            "updated_at": "2026-06-26T01:00:00Z",
                            "raw": raw_book,
                        }
                    ],
                },
                {"variable_name": "count", "variable_value": 1},
                {"variable_name": "total", "variable_value": 1},
            ],
        )

        with patch("tools.list_books.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.list_books.side_effect = BookStackError("Permission denied")
            from_credentials.return_value = client

            error_messages = self.invoke_messages(ListBooksTool, {})

        self.assertEqual(
            error_messages,
            [
                {"variable_name": "success", "variable_value": False},
                {"variable_name": "error", "variable_value": "Permission denied"},
                {"variable_name": "books", "variable_value": []},
                {"variable_name": "count", "variable_value": 0},
                {"variable_name": "total", "variable_value": None},
            ],
        )

    def test_search_pages_outputs_variable_only_success_and_error_payloads(self) -> None:
        with patch("tools.search_pages.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.search_pages.return_value = [{"id": 11, "name": "Runbook", "url": "/pages/11"}]
            from_credentials.return_value = client

            success_payload = self.invoke(SearchPagesTool, {"query": "Runbook"})

        self.assertEqual(success_payload["success"], True)
        self.assertIsNone(success_payload["error"])
        self.assertEqual(success_payload["count"], 1)
        self.assert_payload_keys_match_schema(success_payload, "search_pages")
        self.assert_collection_item_keys_match_schema(success_payload, "search_pages", "results")

        with patch("tools.search_pages.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.search_pages.side_effect = BookStackError("BookStack API unavailable")
            from_credentials.return_value = client

            error_payload = self.invoke(SearchPagesTool, {"query": "Runbook"})

        self.assertEqual(
            error_payload,
            {"success": False, "error": "BookStack API unavailable", "results": [], "count": 0},
        )
        self.assert_payload_keys_match_schema(error_payload, "search_pages")

    def test_get_page_outputs_variable_only_success_and_error_payloads(self) -> None:
        with patch("tools.get_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.get_page.return_value = {
                "id": 12,
                "name": "Ops Runbook",
                "url": "/pages/12",
                "markdown": "# Ops",
                "book_id": 7,
                "chapter_id": 9,
                "slug": "ops-runbook",
                "created_at": "2026-06-26T00:00:00Z",
                "updated_at": "2026-06-26T01:00:00Z",
                "created_by": {"id": 1},
                "updated_by": {"id": 2},
            }
            from_credentials.return_value = client

            success_payload = self.invoke(GetPageTool, {"page_id": "12"})

        self.assertEqual(success_payload["success"], True)
        self.assertIsNone(success_payload["error"])
        self.assertEqual(success_payload["content"], "# Ops")
        self.assertEqual(success_payload["markdown"], "# Ops")
        self.assertEqual(success_payload["content_format"], "markdown")
        self.assert_payload_keys_match_schema(success_payload, "get_page")

        with patch("tools.get_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.get_page.side_effect = BookStackError("Page not found")
            from_credentials.return_value = client

            error_payload = self.invoke(GetPageTool, {"page_id": "12"})

        self.assertEqual(
            error_payload,
            {
                "success": False,
                "error": "Page not found",
                "page_id": None,
                "title": None,
                "url": None,
                "content": None,
                "markdown": None,
                "content_format": None,
                "book_id": None,
                "chapter_id": None,
                "slug": None,
                "created_at": None,
                "updated_at": None,
                "created_by": None,
                "updated_by": None,
                "raw": None,
            },
        )
        self.assert_payload_keys_match_schema(error_payload, "get_page")

    def test_create_page_outputs_variable_only_success_and_error_payloads(self) -> None:
        with patch("tools.create_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.create_page.return_value = {"id": 13, "name": "New Page", "url": "/pages/13"}
            from_credentials.return_value = client

            success_payload = self.invoke(
                CreatePageTool,
                {"title": "New Page", "markdown": "# Body", "book_id": "7"},
            )

        self.assertEqual(success_payload["success"], True)
        self.assertEqual(success_payload["action"], "created")
        self.assert_payload_keys_match_schema(success_payload, "create_page")

        with patch("tools.create_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.create_page.side_effect = BookStackError("Book not found")
            from_credentials.return_value = client

            error_payload = self.invoke(
                CreatePageTool,
                {"title": "New Page", "markdown": "# Body", "book_id": "7"},
            )

        self.assertEqual(
            error_payload,
            {
                "success": False,
                "error": "Book not found",
                "page_id": None,
                "title": None,
                "url": None,
                "action": None,
                "raw": None,
            },
        )
        self.assert_payload_keys_match_schema(error_payload, "create_page")

    def test_update_page_outputs_variable_only_success_and_error_payloads(self) -> None:
        with patch("tools.update_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.update_page.return_value = {"id": 14, "name": "Updated Page", "url": "/pages/14"}
            from_credentials.return_value = client

            success_payload = self.invoke(
                UpdatePageTool,
                {"page_id": "14", "title": "Updated Page"},
            )

        self.assertEqual(success_payload["success"], True)
        self.assertEqual(success_payload["action"], "updated")
        self.assert_payload_keys_match_schema(success_payload, "update_page")

        with patch("tools.update_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.update_page.side_effect = BookStackError("Page not found")
            from_credentials.return_value = client

            error_payload = self.invoke(
                UpdatePageTool,
                {"page_id": "14", "title": "Updated Page"},
            )

        self.assertEqual(
            error_payload,
            {
                "success": False,
                "error": "Page not found",
                "page_id": None,
                "title": None,
                "url": None,
                "action": None,
                "raw": None,
            },
        )
        self.assert_payload_keys_match_schema(error_payload, "update_page")

    def test_publish_page_outputs_variable_only_success_and_error_payloads(self) -> None:
        with patch("tools.publish_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.search_pages.return_value = []
            client.create_page.return_value = {"id": 15, "name": "Published Page", "url": "/pages/15"}
            from_credentials.return_value = client

            success_payload = self.invoke(
                PublishPageTool,
                {"title": "Published Page", "markdown": "# Body", "book_id": "7"},
            )

        self.assertEqual(success_payload["success"], True)
        self.assertEqual(success_payload["action"], "created")
        self.assert_payload_keys_match_schema(success_payload, "publish_page")

        with patch("tools.publish_page.BookStackClient.from_credentials") as from_credentials:
            client = Mock()
            client.search_pages.side_effect = BookStackError("Permission denied")
            from_credentials.return_value = client

            error_payload = self.invoke(
                PublishPageTool,
                {"title": "Published Page", "markdown": "# Body", "book_id": "7"},
            )

        self.assertEqual(
            error_payload,
            {
                "success": False,
                "error": "Permission denied",
                "page_id": None,
                "title": None,
                "url": None,
                "action": None,
                "raw": None,
            },
        )
        self.assert_payload_keys_match_schema(error_payload, "publish_page")


if __name__ == "__main__":
    unittest.main()
