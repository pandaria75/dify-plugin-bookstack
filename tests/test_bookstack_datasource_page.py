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

        class JsonMessage:
            def __init__(self, json_object):
                self.json_object = json_object

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
        }
        request = SimpleNamespace(page_id="42")

        with patch.object(self.bookstack_page_module.BookStackClient, "from_credentials") as from_credentials:
            from_credentials.return_value.get_page.return_value = raw_page

            result = list(self.datasource._get_content(request))

        from_credentials.return_value.get_page.assert_called_once_with("42")
        self.assertEqual(len(result), 1)
        message = result[0]
        self.assertEqual(message.type.value, "json")
        self.assertIsNone(message.meta)
        self.assertEqual(
            message.message.json_object,
            {
                "page_id": "42",
                "title": "Runbook",
                "content": "# Runbook",
                "source_url": "https://example.test/books/ops/page/runbook",
            },
        )

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
        self.assertEqual(
            result[0].message.json_object,
            {
                "page_id": "7",
                "title": "Fallback Title",
                "content": "Legacy body",
                "source_url": "https://example.test/pages/7",
            },
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


if __name__ == "__main__":
    unittest.main()
