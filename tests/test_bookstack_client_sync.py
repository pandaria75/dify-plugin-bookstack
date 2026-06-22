from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import bookstack_client as root_client
import bookstack_datasource.bookstack_client as datasource_client
from scripts import sync_bookstack_client


class FakeResponse:
    def __init__(self, status_code: int, *, content: bytes = b"{}", json_value=None, json_error: Exception | None = None):
        self.status_code = status_code
        self.content = content
        self._json_value = json_value
        self._json_error = json_error

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        return self._json_value


class FakeSession:
    def __init__(self, response: FakeResponse):
        self.headers = {}
        self.request = Mock(return_value=response)


class BookStackClientSyncTestCase(unittest.TestCase):
    def test_generated_datasource_client_matches_rendered_output(self):
        self.assertEqual(
            sync_bookstack_client.render_datasource_client(),
            sync_bookstack_client.TARGET_PATH.read_text(encoding="utf-8"),
        )

    def test_check_mode_detects_drift(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "bookstack_client.py"
            target_path.write_text("drift\n", encoding="utf-8")

            with patch.object(sync_bookstack_client, "TARGET_PATH", target_path):
                with patch.object(sys, "argv", ["sync_bookstack_client.py", "--check"]):
                    self.assertEqual(sync_bookstack_client.main(), 1)

    def test_check_mode_passes_when_generated_file_is_current(self):
        rendered = sync_bookstack_client.render_datasource_client()

        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "bookstack_client.py"
            target_path.write_text(rendered, encoding="utf-8")

            with patch.object(sync_bookstack_client, "TARGET_PATH", target_path):
                with patch.object(sys, "argv", ["sync_bookstack_client.py", "--check"]):
                    self.assertEqual(sync_bookstack_client.main(), 0)

    def test_datasource_client_subset_excludes_tool_only_methods(self):
        expected_methods = {
            "from_credentials",
            "_require_credential",
            "_parse_timeout",
            "_parse_verify_ssl",
            "_api_url",
            "_session",
            "_request",
            "validate_credentials",
            "get_page",
        }
        excluded_methods = {
            "search_pages",
            "list_books",
            "list_shelves",
            "list_pages",
            "list_chapters",
            "_build_page_payload",
            "create_page",
            "update_page",
        }

        for method_name in expected_methods:
            with self.subTest(method_name=method_name):
                self.assertTrue(hasattr(datasource_client.BookStackClient, method_name))

        for method_name in excluded_methods:
            with self.subTest(method_name=method_name):
                self.assertFalse(hasattr(datasource_client.BookStackClient, method_name))

    def test_datasource_client_preserves_shared_error_contract(self):
        cases = [
            ("validate_credentials", 401, "InvalidCredentialsError", "Invalid credentials"),
            ("validate_credentials", 403, "PermissionDeniedError", "Permission denied"),
            ("validate_credentials", 500, "ServiceUnavailableError", "BookStack API unavailable"),
            ("get_page", 404, "PageNotFoundError", "Page not found"),
        ]

        for module in (root_client, datasource_client):
            for operation, status_code, error_name, error_message in cases:
                with self.subTest(module=module.__name__, operation=operation, status_code=status_code):
                    fake_session = FakeSession(FakeResponse(status_code, content=b"{}"))
                    client = module.BookStackClient("https://example.test", "id", "secret")

                    with patch(f"{module.__name__}.requests.Session", return_value=fake_session):
                        with self.assertRaisesRegex(getattr(module, error_name), error_message) as caught:
                            if operation == "validate_credentials":
                                client.validate_credentials()
                            else:
                                client.get_page("42")

                    self.assertEqual(type(caught.exception).__name__, error_name)
                    self.assertEqual(str(caught.exception), error_message)

    def test_datasource_client_preserves_invalid_response_contract(self):
        for module in (root_client, datasource_client):
            with self.subTest(module=module.__name__):
                fake_session = FakeSession(FakeResponse(200, content=b"not-json", json_error=ValueError("bad json")))
                client = module.BookStackClient("https://example.test", "id", "secret")

                with patch(f"{module.__name__}.requests.Session", return_value=fake_session):
                    with self.assertRaisesRegex(module.InvalidResponseError, "Invalid BookStack response") as caught:
                        client.validate_credentials()

                self.assertEqual(type(caught.exception).__name__, "InvalidResponseError")
                self.assertEqual(str(caught.exception), "Invalid BookStack response")


if __name__ == "__main__":
    unittest.main()
