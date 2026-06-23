from __future__ import annotations

import importlib
import sys
import types
import unittest
from enum import Enum
from types import SimpleNamespace
from unittest.mock import patch

from bookstack_datasource.bookstack_client import InvalidCredentialsError, PageNotFoundError


def _install_fake_dify_plugin() -> dict[str, types.ModuleType | None]:
    module_names = [
        "dify_plugin",
        "dify_plugin.entities",
        "dify_plugin.entities.datasource",
        "dify_plugin.interfaces",
        "dify_plugin.interfaces.datasource",
        "dify_plugin.interfaces.datasource.online_document",
    ]
    previous_modules = {name: sys.modules.get(name) for name in module_names}

    dify_plugin = types.ModuleType("dify_plugin")
    entities = types.ModuleType("dify_plugin.entities")
    datasource_entities = types.ModuleType("dify_plugin.entities.datasource")
    interfaces = types.ModuleType("dify_plugin.interfaces")
    datasource_interfaces = types.ModuleType("dify_plugin.interfaces.datasource")
    online_document = types.ModuleType("dify_plugin.interfaces.datasource.online_document")

    class DatasourceGetPagesResponse:
        def __init__(self, result):
            self.result = result

    class DatasourceMessage:
        class MessageType(Enum):
            JSON = "json"
            TEXT = "text"

        class JsonMessage:
            def __init__(self, json_object):
                self.json_object = json_object

        class TextMessage:
            def __init__(self, text):
                self.text = text

        def __init__(self, type, message, meta=None):
            self.type = type
            self.message = message
            self.meta = meta

    class OnlineDocumentInfo:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class OnlineDocumentPage:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class OnlineDocumentDatasource:
        def __init__(self):
            self.runtime = SimpleNamespace(credentials={})

        def __init_subclass__(cls, **kwargs):
            pass

    class GetOnlineDocumentPageContentRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    # Real SDK layout:
    #   entities.datasource has: DatasourceGetPagesResponse, DatasourceMessage,
    #       GetOnlineDocumentPageContentRequest, OnlineDocumentInfo, OnlineDocumentPage
    #   interfaces.datasource.online_document has: OnlineDocumentDatasource
    datasource_entities.DatasourceGetPagesResponse = DatasourceGetPagesResponse
    datasource_entities.DatasourceMessage = DatasourceMessage
    datasource_entities.GetOnlineDocumentPageContentRequest = GetOnlineDocumentPageContentRequest
    datasource_entities.OnlineDocumentInfo = OnlineDocumentInfo
    datasource_entities.OnlineDocumentPage = OnlineDocumentPage
    online_document.OnlineDocumentDatasource = OnlineDocumentDatasource

    sys.modules["dify_plugin"] = dify_plugin
    sys.modules["dify_plugin.entities"] = entities
    sys.modules["dify_plugin.entities.datasource"] = datasource_entities
    sys.modules["dify_plugin.interfaces"] = interfaces
    sys.modules["dify_plugin.interfaces.datasource"] = datasource_interfaces
    sys.modules["dify_plugin.interfaces.datasource.online_document"] = online_document

    return previous_modules


def _restore_modules(previous_modules: dict[str, types.ModuleType | None]) -> None:
    for name, module in previous_modules.items():
        if module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module
    sys.modules.pop("bookstack_datasource.datasources.bookstack_page", None)
    sys.modules.pop("bookstack_datasource.datasources.bookstack_chapter", None)
    sys.modules.pop("bookstack_datasource.datasources.bookstack_book", None)
    sys.modules.pop("bookstack_datasource.datasources._metadata", None)


def _expected_meta(**overrides):
    meta = {
        "source": "bookstack",
        "sync_scope": None,
        "sync_source_id": None,
        "page_id": None,
        "bookstack_page_id": None,
        "bookstack_book_id": None,
        "bookstack_chapter_id": None,
        "title": None,
        "url": None,
        "source_url": None,
        "tags": [],
        "created_at": None,
        "updated_at": None,
        "content_format": None,
        "parent_id": None,
    }
    meta.update(overrides)
    return meta


class BookStackPageDatasourceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_modules = _install_fake_dify_plugin()
        cls.bookstack_page_module = importlib.import_module("bookstack_datasource.datasources.bookstack_page")
        cls.datasource_class = cls.bookstack_page_module.BookStackPageDatasource

    @classmethod
    def tearDownClass(cls):
        _restore_modules(cls.previous_modules)

    def setUp(self):
        self.datasource = self.datasource_class()
        self.datasource.runtime.credentials = {
            "base_url": "https://example.test",
            "token_id": "id",
            "token_secret": "secret",
        }

    def test_get_pages_returns_online_document_contract_shape(self):
        raw_page = {
            "id": 42,
            "name": "Runbook",
            "url": "https://example.test/books/ops/page/runbook",
        }

        with patch.object(self.bookstack_page_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            response = self.datasource._get_pages({"page_id": "42"})

        from_credentials.assert_called_once_with(self.datasource.runtime.credentials)
        from_credentials.return_value.get_page.assert_called_once_with("42")
        self.assertEqual(len(response.result), 1)

        workspace = response.result[0]
        self.assertEqual(workspace.workspace_id, "42")
        self.assertEqual(workspace.workspace_name, "Runbook")
        self.assertEqual(workspace.workspace_icon, "")
        self.assertEqual(workspace.total, 1)
        self.assertEqual(len(workspace.pages), 1)

        page = workspace.pages[0]
        self.assertEqual(page.page_id, "42")
        self.assertEqual(page.page_name, "Runbook")
        self.assertIsNone(page.page_icon)
        self.assertEqual(page.type, "page")
        self.assertEqual(page.last_edited_time, "")
        self.assertIsNone(page.parent_id)

    def test_get_pages_rejects_missing_page_id(self):
        with self.assertRaisesRegex(ValueError, "page_id is required"):
            self.datasource._get_pages({})

    def test_get_content_yields_datasource_json_message(self):
        raw_page = {
            "id": 42,
            "name": "Runbook",
            "markdown": "# Runbook",
            "url": "https://example.test/books/ops/page/runbook",
            "tags": [{"name": "ops"}, {"name": "runbook"}],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }
        request = SimpleNamespace(page_id="42")

        with patch.object(self.bookstack_page_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        from_credentials.return_value.get_page.assert_called_once_with("42")
        self.assertEqual(len(result), 1)
        message = result[0]
        self.assertEqual(message.type.value, "text")
        self.assertEqual(
            message.meta,
            _expected_meta(
                sync_scope="page",
                sync_source_id="42",
                page_id="42",
                bookstack_page_id="42",
                title="Runbook",
                url="https://example.test/books/ops/page/runbook",
                source_url="https://example.test/books/ops/page/runbook",
                tags=["ops", "runbook"],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
                content_format="markdown",
            ),
        )
        self.assertEqual(message.message.text, "# Runbook")

    def test_get_content_accepts_nested_page_identity(self):
        raw_page = {
            "id": 7,
            "title": "Fallback Title",
            "body": "Legacy body",
            "url": "https://example.test/pages/7",
        }
        request = SimpleNamespace(page=SimpleNamespace(id="7"))

        with patch.object(self.bookstack_page_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].message.text, "Legacy body")
        self.assertEqual(
            result[0].meta,
            _expected_meta(
                sync_scope="page",
                sync_source_id="7",
                page_id="7",
                bookstack_page_id="7",
                title="Fallback Title",
                url="https://example.test/pages/7",
                source_url="https://example.test/pages/7",
                content_format="body",
            ),
        )

    def test_get_content_without_page_id_in_payload_falls_back_to_request_identity(self):
        raw_page = {
            "title": "Untitled Remote Page",
            "url": "https://example.test/pages/42",
        }
        request = SimpleNamespace(page_id="42")

        with patch.object(self.bookstack_page_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        self.assertEqual(result[0].message.text, "")
        self.assertEqual(
            result[0].meta,
            _expected_meta(
                sync_scope="page",
                sync_source_id="42",
                page_id="42",
                bookstack_page_id="42",
                title="Untitled Remote Page",
                url="https://example.test/pages/42",
                source_url="https://example.test/pages/42",
                content_format=None,
            ),
        )

    def test_get_pages_propagates_bookstack_errors(self):
        with patch.object(self.bookstack_page_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.side_effect = PageNotFoundError("Page not found")

            with self.assertRaisesRegex(PageNotFoundError, "Page not found"):
                self.datasource._get_pages({"page_id": "404"})

    def test_get_content_propagates_invalid_credentials(self):
        request = SimpleNamespace(page_id="42")

        with patch.object(self.bookstack_page_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.side_effect = InvalidCredentialsError("Invalid credentials")

            with self.assertRaisesRegex(InvalidCredentialsError, "Invalid credentials"):
                list(self.datasource._get_content(request))


class BookStackChapterDatasourceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_modules = _install_fake_dify_plugin()
        cls.bookstack_chapter_module = importlib.import_module(
            "bookstack_datasource.datasources.bookstack_chapter"
        )
        cls.datasource_class = cls.bookstack_chapter_module.BookStackChapterDatasource

    @classmethod
    def tearDownClass(cls):
        _restore_modules(cls.previous_modules)

    def setUp(self):
        self.datasource = self.datasource_class()
        self.datasource.runtime.credentials = {
            "base_url": "https://example.test",
            "token_id": "id",
            "token_secret": "secret",
        }

    def test_get_pages_rejects_missing_chapter_id(self):
        with self.assertRaisesRegex(ValueError, "chapter_id is required"):
            self.datasource._get_pages({})

    def test_get_pages_returns_multiple_pages_with_parent_ids(self):
        raw_pages = {
            "data": [
                {
                    "id": 11,
                    "name": "Chapter Intro",
                    "chapter": {"id": 7, "name": "Operations"},
                },
                {
                    "id": 12,
                    "title": "Runbook",
                    "chapter_id": 7,
                },
            ]
        }

        with patch.object(self.bookstack_chapter_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.list_pages.return_value = raw_pages

            response = self.datasource._get_pages({"chapter_id": "7"})

        from_credentials.assert_called_once_with(self.datasource.runtime.credentials)
        from_credentials.return_value.list_pages.assert_called_once_with(chapter_id="7")
        self.assertEqual(len(response.result), 1)

        workspace = response.result[0]
        self.assertEqual(workspace.workspace_id, "7")
        self.assertEqual(workspace.workspace_name, "Operations")
        self.assertEqual(workspace.workspace_icon, "")
        self.assertEqual(workspace.total, 2)
        self.assertEqual([page.page_id for page in workspace.pages], ["11", "12"])
        self.assertEqual([page.page_name for page in workspace.pages], ["Chapter Intro", "Runbook"])
        self.assertEqual([page.parent_id for page in workspace.pages], ["7", "7"])

    def test_get_content_accepts_chapter_emitted_page_identity(self):
        raw_page = {
            "id": 12,
            "name": "Runbook",
            "markdown": "# Runbook",
            "url": "https://example.test/books/ops/page/runbook",
            "chapter_id": 7,
            "book_id": 2,
        }
        request = SimpleNamespace(page=SimpleNamespace(id="12", parent_id="7"))

        with patch.object(self.bookstack_chapter_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        from_credentials.return_value.get_page.assert_called_once_with("12")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].message.text, "# Runbook")
        self.assertEqual(
            result[0].meta,
            _expected_meta(
                sync_scope="chapter",
                sync_source_id="7",
                page_id="12",
                bookstack_page_id="12",
                bookstack_book_id="2",
                bookstack_chapter_id="7",
                parent_id="7",
                title="Runbook",
                url="https://example.test/books/ops/page/runbook",
                source_url="https://example.test/books/ops/page/runbook",
                content_format="markdown",
            ),
        )

    def test_get_content_without_parent_context_keeps_parent_id_key(self):
        raw_page = {
            "id": 12,
            "name": "Runbook",
            "html": "<p>Runbook</p>",
            "url": "https://example.test/books/ops/page/runbook",
            "book_id": 2,
        }
        request = SimpleNamespace(page_id="12")

        with patch.object(self.bookstack_chapter_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        self.assertEqual(result[0].message.text, "<p>Runbook</p>")
        self.assertEqual(
            result[0].meta,
            _expected_meta(
                sync_scope="chapter",
                sync_source_id="12",
                page_id="12",
                bookstack_page_id="12",
                bookstack_book_id="2",
                bookstack_chapter_id=None,
                parent_id=None,
                title="Runbook",
                url="https://example.test/books/ops/page/runbook",
                source_url="https://example.test/books/ops/page/runbook",
                content_format="html",
            ),
        )

    def test_get_pages_propagates_bookstack_errors(self):
        with patch.object(self.bookstack_chapter_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.list_pages.side_effect = InvalidCredentialsError(
                "Invalid credentials"
            )

            with self.assertRaisesRegex(InvalidCredentialsError, "Invalid credentials"):
                self.datasource._get_pages({"chapter_id": "7"})

    def test_get_content_propagates_page_lookup_errors(self):
        request = SimpleNamespace(page_id="12")

        with patch.object(self.bookstack_chapter_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.side_effect = PageNotFoundError("Page not found")

            with self.assertRaisesRegex(PageNotFoundError, "Page not found"):
                list(self.datasource._get_content(request))


class BookStackBookDatasourceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_modules = _install_fake_dify_plugin()
        cls.bookstack_book_module = importlib.import_module(
            "bookstack_datasource.datasources.bookstack_book"
        )
        cls.datasource_class = cls.bookstack_book_module.BookStackBookDatasource

    @classmethod
    def tearDownClass(cls):
        _restore_modules(cls.previous_modules)

    def setUp(self):
        self.datasource = self.datasource_class()
        self.datasource.runtime.credentials = {
            "base_url": "https://example.test",
            "token_id": "id",
            "token_secret": "secret",
        }

    def test_get_pages_rejects_missing_book_id(self):
        with self.assertRaisesRegex(ValueError, "book_id is required"):
            self.datasource._get_pages({})

    def test_get_pages_returns_multiple_pages_with_parent_ids_and_pagination(self):
        first_batch = {
            "total": 3,
            "data": [
                {
                    "id": 21,
                    "name": "Intro",
                    "chapter": {"id": 701, "name": "Operations"},
                    "book": {"id": 77, "name": "Ops Handbook"},
                },
                {
                    "id": 22,
                    "title": "Runbook",
                    "chapter_id": 702,
                    "book_id": 77,
                },
            ],
        }
        second_batch = {
            "total": 3,
            "data": [
                {
                    "id": 23,
                    "name": "Appendix",
                    "book": {"id": 77, "name": "Ops Handbook"},
                }
            ],
        }

        with patch.object(self.bookstack_book_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.list_pages.side_effect = [first_batch, second_batch]

            response = self.datasource._get_pages({"book_id": "77"})

        from_credentials.assert_called_once_with(self.datasource.runtime.credentials)
        self.assertEqual(
            from_credentials.return_value.list_pages.call_args_list,
            [
                unittest.mock.call(book_id="77", count=100, offset=0),
                unittest.mock.call(book_id="77", count=100, offset=2),
            ],
        )
        self.assertEqual(len(response.result), 1)

        workspace = response.result[0]
        self.assertEqual(workspace.workspace_id, "77")
        self.assertEqual(workspace.workspace_name, "Ops Handbook")
        self.assertEqual(workspace.workspace_icon, "")
        self.assertEqual(workspace.total, 3)
        self.assertEqual([page.page_id for page in workspace.pages], ["21", "22", "23"])
        self.assertEqual([page.page_name for page in workspace.pages], ["Intro", "Runbook", "Appendix"])
        self.assertEqual([page.parent_id for page in workspace.pages], ["701", "702", "77"])

    def test_get_pages_returns_empty_book_workspace(self):
        with patch.object(self.bookstack_book_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.list_pages.return_value = {"data": []}

            response = self.datasource._get_pages({"book_id": "77"})

        workspace = response.result[0]
        self.assertEqual(workspace.workspace_id, "77")
        self.assertEqual(workspace.workspace_name, "Book 77")
        self.assertEqual(workspace.total, 0)
        self.assertEqual(workspace.pages, [])

    def test_get_content_accepts_book_emitted_page_identity(self):
        raw_page = {
            "id": 23,
            "name": "Appendix",
            "markdown": "# Appendix",
            "url": "https://example.test/books/ops/page/appendix",
            "book_id": 77,
        }
        request = SimpleNamespace(page=SimpleNamespace(id="23", parent_id="77"))

        with patch.object(self.bookstack_book_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        from_credentials.return_value.get_page.assert_called_once_with("23")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].message.text, "# Appendix")
        self.assertEqual(
            result[0].meta,
            _expected_meta(
                sync_scope="book",
                sync_source_id="77",
                page_id="23",
                bookstack_page_id="23",
                bookstack_book_id="77",
                parent_id="77",
                title="Appendix",
                url="https://example.test/books/ops/page/appendix",
                source_url="https://example.test/books/ops/page/appendix",
                content_format="markdown",
            ),
        )

    def test_get_content_without_parent_context_uses_stable_null_parent_id(self):
        raw_page = {
            "id": 23,
            "name": "Appendix",
            "body": "Appendix body",
            "url": "https://example.test/books/ops/page/appendix",
            "tags": ["appendix"],
        }
        request = SimpleNamespace(page_id="23")

        with patch.object(self.bookstack_book_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        self.assertEqual(result[0].message.text, "Appendix body")
        self.assertEqual(
            result[0].meta,
            _expected_meta(
                sync_scope="book",
                sync_source_id="23",
                page_id="23",
                bookstack_page_id="23",
                bookstack_book_id=None,
                bookstack_chapter_id=None,
                parent_id=None,
                title="Appendix",
                url="https://example.test/books/ops/page/appendix",
                source_url="https://example.test/books/ops/page/appendix",
                tags=["appendix"],
                content_format="body",
            ),
        )

    def test_get_pages_propagates_bookstack_errors(self):
        with patch.object(self.bookstack_book_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.list_pages.side_effect = InvalidCredentialsError(
                "Invalid credentials"
            )

            with self.assertRaisesRegex(InvalidCredentialsError, "Invalid credentials"):
                self.datasource._get_pages({"book_id": "77"})

    def test_get_content_propagates_page_lookup_errors(self):
        request = SimpleNamespace(page_id="23")

        with patch.object(self.bookstack_book_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.side_effect = PageNotFoundError("Page not found")

            with self.assertRaisesRegex(PageNotFoundError, "Page not found"):
                list(self.datasource._get_content(request))


if __name__ == "__main__":
    unittest.main()
