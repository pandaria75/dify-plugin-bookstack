from __future__ import annotations

import unittest
from unittest.mock import patch

from bookstack_client import BookStackClient, PageNotFoundError
from tools.update_page import normalize_updated_page_result


class UpdatePageMappingTestCase(unittest.TestCase):
    def test_normalize_updated_page_result_returns_required_fields_and_raw(self):
        raw = {
            "id": 42,
            "name": "Ops Runbook",
            "url": "https://example.test/books/ops/page/ops-runbook",
        }

        normalized = normalize_updated_page_result(raw)

        self.assertEqual(normalized["page_id"], 42)
        self.assertEqual(normalized["title"], "Ops Runbook")
        self.assertEqual(normalized["url"], "https://example.test/books/ops/page/ops-runbook")
        self.assertEqual(normalized["action"], "updated")
        self.assertIs(normalized["raw"], raw)


class UpdatePageClientTestCase(unittest.TestCase):
    def test_update_page_sends_optional_location_changes(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"id": 42}) as request:
            result = client.update_page(
                "42",
                title="Updated Title",
                markdown="# Updated",
                tags=["ops"],
                book_id="7",
                chapter_id="11",
            )

        request.assert_called_once_with(
            "PUT",
            "pages/42",
            json={
                "name": "Updated Title",
                "markdown": "# Updated",
                "tags": ["ops"],
                "book_id": "7",
                "chapter_id": "11",
            },
            not_found_error=PageNotFoundError,
            not_found_message="Page not found",
        )
        self.assertEqual(result, {"id": 42})


if __name__ == "__main__":
    unittest.main()
