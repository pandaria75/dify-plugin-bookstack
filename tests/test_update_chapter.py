from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from bookstack_client import BookStackClient, ChapterNotFoundError
from tools.update_chapter import UpdateChapterTool, normalize_updated_chapter_result


class UpdateChapterMappingTestCase(unittest.TestCase):
    def test_normalize_updated_chapter_result_adds_action_and_raw(self):
        raw = {
            "id": 11,
            "name": "Runbooks",
            "slug": "runbooks",
            "book_id": 7,
            "url": "https://example.test/chapters/runbooks",
        }

        normalized = normalize_updated_chapter_result(raw)

        self.assertEqual(normalized["chapter_id"], 11)
        self.assertEqual(normalized["action"], "updated")
        self.assertIs(normalized["raw"], raw)


class UpdateChapterClientTestCase(unittest.TestCase):
    def test_update_chapter_sends_normalized_resource_payload(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 11}) as request:
            result = client.update_chapter(
                "11",
                name="Runbooks",
                description="Ops docs",
                description_html="<p>Ops docs</p>",
                tags=[{"name": "team", "value": "ops"}],
                priority=5,
            )

        request.assert_called_once_with(
            "PUT",
            "chapters/11",
            json={
                "name": "Runbooks",
                "description": "Ops docs",
                "description_html": "<p>Ops docs</p>",
                "tags": [{"name": "team", "value": "ops"}],
                "priority": 5,
            },
            not_found_error=ChapterNotFoundError,
            not_found_message="Chapter not found",
        )
        self.assertEqual(result, {"id": 11})


class UpdateChapterToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = object.__new__(UpdateChapterTool)
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

    @patch("tools.update_chapter.BookStackClient.from_credentials")
    def test_requires_chapter_id(self, from_credentials: Mock) -> None:
        result = self._invoke(chapter_id="   ", name="Runbooks")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "chapter_id is required")

    @patch("tools.update_chapter.BookStackClient.from_credentials")
    def test_requires_at_least_one_non_empty_update_field(self, from_credentials: Mock) -> None:
        result = self._invoke(chapter_id="11", description="   ")

        from_credentials.assert_not_called()
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "at least one update field is required")

    @patch("tools.update_chapter.BookStackClient.from_credentials")
    def test_normalizes_and_forwards_updates(self, from_credentials: Mock) -> None:
        client = Mock()
        client.update_chapter.return_value = {"id": 11, "name": "Runbooks", "slug": "runbooks", "book_id": 7}
        from_credentials.return_value = client

        result = self._invoke(
            chapter_id=" 11 ",
            name=" Runbooks ",
            description=" Ops docs ",
            description_html=" <p>Ops docs</p> ",
            tags="team:ops",
            priority="10",
        )

        client.update_chapter.assert_called_once_with(
            "11",
            name="Runbooks",
            description="Ops docs",
            description_html="<p>Ops docs</p>",
            tags=[{"name": "team", "value": "ops"}],
            priority=10,
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(result["action"], "updated")


if __name__ == "__main__":
    unittest.main()
