from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, BookNotFoundError
from tools.create_chapter import CreateChapterTool, normalize_created_chapter_result


class CreateChapterMappingTestCase(unittest.TestCase):
    def test_normalize_created_chapter_result_adds_action_and_raw(self):
        raw = {
            "id": 11,
            "name": "Runbooks",
            "slug": "runbooks",
            "book_id": 7,
            "url": "https://example.test/chapters/runbooks",
        }

        normalized = normalize_created_chapter_result(raw)

        self.assertEqual(normalized["chapter_id"], 11)
        self.assertEqual(normalized["action"], "created")
        self.assertIs(normalized["raw"], raw)


class CreateChapterClientTestCase(unittest.TestCase):
    def test_create_chapter_sends_normalized_resource_payload(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 11}) as request:
            result = client.create_chapter(
                book_id="7",
                name="Runbooks",
                description="Ops docs",
                description_html="<p>Ops docs</p>",
                tags=[{"name": "team", "value": "ops"}],
                priority=5,
            )

        request.assert_called_once_with(
            "POST",
            "chapters",
            json={
                "book_id": "7",
                "name": "Runbooks",
                "description": "Ops docs",
                "description_html": "<p>Ops docs</p>",
                "tags": [{"name": "team", "value": "ops"}],
                "priority": 5,
            },
            not_found_error=BookNotFoundError,
            not_found_message="Book not found",
        )
        self.assertEqual(result, {"id": 11})


class CreateChapterToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(CreateChapterTool)
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

    @patch("tools.create_chapter.BookStackClient.from_credentials")
    def test_requires_book_id(self, from_credentials: Mock) -> None:
        result = self._invoke(book_id="   ", name="Runbooks")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "book_id is required")

    @patch("tools.create_chapter.BookStackClient.from_credentials")
    def test_normalizes_optional_fields_tags_and_priority(self, from_credentials: Mock) -> None:
        client = Mock()
        client.create_chapter.return_value = {"id": 11, "name": "Runbooks", "slug": "runbooks", "book_id": 7}
        from_credentials.return_value = client

        result = self._invoke(
            book_id=" 7 ",
            name=" Runbooks ",
            description=" Ops docs ",
            description_html=" <p>Ops docs</p> ",
            tags=["team:ops", "status:active"],
            priority="10",
        )

        client.create_chapter.assert_called_once_with(
            book_id="7",
            name="Runbooks",
            description="Ops docs",
            description_html="<p>Ops docs</p>",
            tags=[
                {"name": "team", "value": "ops"},
                {"name": "status", "value": "active"},
            ],
            priority=10,
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "created")


if __name__ == "__main__":
    unittest.main()
