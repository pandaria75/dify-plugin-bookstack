from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

from bookstack_client import (
    BookNotFoundError,
    BookStackClient,
    ChapterNotFoundError,
    InvalidCredentialsError,
    InvalidQueryError,
    InvalidResponseError,
    PageNotFoundError,
    PermissionDeniedError,
    ShelfNotFoundError,
    ServiceUnavailableError,
)


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
        self._response = response
        self.request = Mock(return_value=response)


class BookStackClientTestCase(unittest.TestCase):
    def test_from_credentials_parses_timeout_and_ssl(self):
        client = BookStackClient.from_credentials(
            {
                "base_url": "https://example.test/",
                "token_id": "id",
                "token_secret": "secret",
                "timeout_seconds": "12.5",
                "verify_ssl": "false",
            }
        )

        self.assertEqual(client.base_url, "https://example.test/")
        self.assertEqual(client.token_id, "id")
        self.assertEqual(client.token_secret, "secret")
        self.assertEqual(client.timeout_seconds, 12.5)
        self.assertFalse(client.verify_ssl)

    def test_from_credentials_rejects_missing_required_fields(self):
        with self.assertRaisesRegex(InvalidCredentialsError, "Invalid credentials"):
            BookStackClient.from_credentials({"token_id": "id", "token_secret": "secret"})

    def test_request_normalizes_url_and_sets_auth_header(self):
        response = FakeResponse(200, content=b'{"ok": true}', json_value={"ok": True})
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret", timeout_seconds=7.0, verify_ssl=False)

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            payload = client._request("GET", "system")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(fake_session.headers["Authorization"], "Token id:secret")
        fake_session.request.assert_called_once_with(
            method="GET",
            url="https://example.test/api/system",
            timeout=7.0,
            verify=False,
        )

    def test_request_404_uses_neutral_default_message(self):
        response = FakeResponse(404, content=b"{}")
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            with self.assertRaisesRegex(BookNotFoundError, "Resource not found"):
                client._request("GET", "system")

    def test_request_404_honors_explicit_not_found_override(self):
        response = FakeResponse(404, content=b"{}")
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            with self.assertRaisesRegex(BookNotFoundError, "Book not found"):
                client._request("GET", "books/1", not_found_message="Book not found")

    def test_request_maps_common_errors(self):
        client = BookStackClient("https://example.test", "id", "secret")

        cases = [
            (401, InvalidCredentialsError, "Invalid credentials"),
            (403, PermissionDeniedError, "Permission denied"),
            (429, ServiceUnavailableError, "BookStack API unavailable"),
            (500, ServiceUnavailableError, "BookStack API unavailable"),
            (418, ServiceUnavailableError, "BookStack API unavailable"),
        ]

        for status_code, error_type, message in cases:
            with self.subTest(status_code=status_code):
                fake_session = FakeSession(FakeResponse(status_code, content=b"{}"))
                with patch("bookstack_client.requests.Session", return_value=fake_session):
                    with self.assertRaisesRegex(error_type, message):
                        client._request("GET", "system")

    def test_request_maps_400_and_422_to_invalid_response(self):
        client = BookStackClient("https://example.test", "id", "secret")

        for status_code in (400, 422):
            with self.subTest(status_code=status_code):
                fake_session = FakeSession(FakeResponse(status_code, content=b"{}"))
                with patch("bookstack_client.requests.Session", return_value=fake_session):
                    with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                        client._request("POST", "pages")

    def test_request_maps_timeout_and_connection_errors_to_service_unavailable(self):
        client = BookStackClient("https://example.test", "id", "secret")

        for request_error in (requests.Timeout("timed out"), requests.ConnectionError("offline")):
            with self.subTest(error_type=type(request_error).__name__):
                fake_session = Mock()
                fake_session.headers = {}
                fake_session.request = Mock(side_effect=request_error)
                with patch("bookstack_client.requests.Session", return_value=fake_session):
                    with self.assertRaisesRegex(ServiceUnavailableError, "BookStack API unavailable"):
                        client._request("GET", "system")

    def test_request_rejects_non_object_json(self):
        response = FakeResponse(200, content=b"[]", json_value=[])
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client._request("GET", "system")

    def test_get_page_404_uses_page_not_found(self):
        response = FakeResponse(404, content=b"{}")
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            with self.assertRaisesRegex(PageNotFoundError, "Page not found"):
                client.get_page("123")

    def test_get_resource_methods_use_resource_specific_not_found_errors(self):
        client = BookStackClient("https://example.test", "id", "secret")

        cases = [
            (client.get_book, ("7",), BookNotFoundError, "Book not found"),
            (client.get_chapter, ("11",), ChapterNotFoundError, "Chapter not found"),
            (client.get_shelf, ("13",), ShelfNotFoundError, "Shelf not found"),
        ]

        for method, args, error_type, message in cases:
            with self.subTest(method=method.__name__):
                fake_session = FakeSession(FakeResponse(404, content=b"{}"))
                with patch("bookstack_client.requests.Session", return_value=fake_session):
                    with self.assertRaisesRegex(error_type, message):
                        method(*args)

    def test_list_chapters_404_uses_book_not_found(self):
        response = FakeResponse(404, content=b"{}")
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            with self.assertRaisesRegex(BookNotFoundError, "Book not found"):
                client.list_chapters(book_id="7")

    def test_list_pages_passes_traversal_filters_and_pagination(self):
        response = FakeResponse(200, content=b'{"data": []}', json_value={"data": []})
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            payload = client.list_pages(book_id="7", chapter_id="11", count=100, offset=200)

        self.assertEqual(payload, {"data": []})
        fake_session.request.assert_called_once_with(
            method="GET",
            url="https://example.test/api/pages",
            timeout=10.0,
            verify=True,
            params={
                "filter[book_id:eq]": "7",
                "filter[chapter_id:eq]": "11",
                "count": 100,
                "offset": 200,
            },
        )

    def test_list_methods_preserve_existing_behavior_without_sort_or_filters(self):
        client = BookStackClient("https://example.test", "id", "secret")

        cases = [
            (client.list_books, {}, ("GET", "books"), {}),
            (client.list_shelves, {}, ("GET", "shelves"), {}),
            (
                client.list_chapters,
                {"book_id": "7", "count": 25, "offset": 50},
                ("GET", "chapters"),
                {
                    "not_found_error": BookNotFoundError,
                    "not_found_message": "Book not found",
                    "params": {"filter[book_id:eq]": "7", "count": 25, "offset": 50},
                },
            ),
            (
                client.list_pages,
                {"book_id": "7", "chapter_id": "11", "count": 25, "offset": 50},
                ("GET", "pages"),
                {
                    "params": {
                        "filter[book_id:eq]": "7",
                        "filter[chapter_id:eq]": "11",
                        "count": 25,
                        "offset": 50,
                    }
                },
            ),
        ]

        for method, kwargs, call_args, extra_kwargs in cases:
            with self.subTest(method=method.__name__):
                with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
                    result = method(**kwargs)

                request.assert_called_once_with(*call_args, **extra_kwargs)
                self.assertEqual(result, {"data": []})

    def test_list_sort_normalizes_plus_minus_and_bare_field(self):
        client = BookStackClient("https://example.test", "id", "secret")

        cases = [
            (client.list_books, {"sort": "+name"}, {"sort": "name"}),
            (client.list_chapters, {"sort": "-priority"}, {"sort": "-priority"}),
            (client.list_pages, {"sort": "updated_at"}, {"sort": "updated_at"}),
        ]

        for method, kwargs, expected_params in cases:
            with self.subTest(method=method.__name__, sort=kwargs["sort"]):
                with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
                    method(**kwargs)

                self.assertEqual(request.call_args.kwargs["params"], expected_params)

    def test_list_filters_map_to_bookstack_filter_query_params(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            client.list_pages(filters='{"name:like":"%Guide%","updated_at:eq":"2026-06-18T00:00:00Z"}')

        request.assert_called_once_with(
            "GET",
            "pages",
            params={
                "filter[name:like]": "%Guide%",
                "filter[updated_at:eq]": "2026-06-18T00:00:00Z",
            },
        )

    def test_list_filters_allow_legacy_scope_when_equal(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            client.list_pages(book_id="7", filters='{"book_id:eq":"7"}')

        request.assert_called_once_with("GET", "pages", params={"filter[book_id:eq]": "7"})

    def test_list_filters_reject_invalid_inputs_before_request_dispatch(self):
        client = BookStackClient("https://example.test", "id", "secret")

        cases = [
            (client.list_books, {"filters": "{"}, "filters must be a valid JSON object string"),
            (client.list_books, {"filters": '["bad"]'}, "filters must be a valid JSON object string"),
            (client.list_books, {"filters": '{"priority:eq":1}'}, "unsupported filter field: priority"),
            (client.list_books, {"filters": '{"name:gt":"Ops"}'}, "unsupported filter operator: gt"),
            (client.list_books, {"filters": '{"filter[name:eq]":"Ops"}'}, "raw filter keys are not allowed"),
            (client.list_books, {"filters": '{"name":"Ops"}'}, "filters keys must use field:operator format"),
            (client.list_books, {"filters": '{"name:eq":["Ops"]}'}, "filters values cannot be lists"),
            (client.list_books, {"filters": '{"name:eq":{"value":"Ops"}}'}, "filters values cannot be objects"),
            (client.list_books, {"filters": '{"name:eq":null}'}, "filters values cannot be null"),
            (client.list_pages, {"book_id": "7", "filters": '{"book_id:eq":"8"}'}, "filters conflict with legacy book_id"),
            (client.list_books, {"sort": "priority"}, "unsupported sort field: priority"),
            (client.list_books, {"sort": "name desc"}, r"sort must use \+field, -field, or field format"),
        ]

        for method, kwargs, message in cases:
            with self.subTest(method=method.__name__, kwargs=kwargs):
                with patch.object(BookStackClient, "_request") as request:
                    with self.assertRaisesRegex(InvalidQueryError, message):
                        method(**kwargs)
                request.assert_not_called()

    def test_list_pages_omits_filter_params_when_filters_not_provided(self):
        response = FakeResponse(200, content=b'{"data": []}', json_value={"data": []})
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            payload = client.list_pages(count=100, offset=200)

        self.assertEqual(payload, {"data": []})
        fake_session.request.assert_called_once_with(
            method="GET",
            url="https://example.test/api/pages",
            timeout=10.0,
            verify=True,
            params={"count": 100, "offset": 200},
        )

    def test_list_chapters_passes_book_scope_and_pagination(self):
        response = FakeResponse(200, content=b'{"data": []}', json_value={"data": []})
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            payload = client.list_chapters(book_id="7", count=25, offset=50)

        self.assertEqual(payload, {"data": []})
        fake_session.request.assert_called_once_with(
            method="GET",
            url="https://example.test/api/chapters",
            timeout=10.0,
            verify=True,
            params={"filter[book_id:eq]": "7", "count": 25, "offset": 50},
        )

    def test_find_books_uses_exact_name_filter(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.find_books("Operations", match="exact", count=25, offset=50)

        request.assert_called_once_with(
            "GET",
            "books",
            params={"filter[name:eq]": "Operations", "count": 25, "offset": 50},
        )
        self.assertEqual(result, {"data": [], "total": 0})

    def test_find_shelves_uses_like_name_filter(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            result = client.find_shelves("Engineering", match="like")

        request.assert_called_once_with(
            "GET",
            "shelves",
            params={"filter[name:like]": "%Engineering%"},
        )
        self.assertEqual(result, {"data": []})

    def test_find_chapters_uses_exact_name_filter_and_book_scope(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            result = client.find_chapters("Runbooks", match="exact", book_id="7", count=25, offset=50)

        request.assert_called_once_with(
            "GET",
            "chapters",
            params={"filter[name:eq]": "Runbooks", "filter[book_id:eq]": "7", "count": 25, "offset": 50},
        )
        self.assertEqual(result, {"data": [], "total": 0})

    def test_find_pages_uses_like_name_filter_with_book_and_chapter_scope(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": []}) as request:
            result = client.find_pages("On Call", match="like", book_id="7", chapter_id="11")

        request.assert_called_once_with(
            "GET",
            "pages",
            params={
                "filter[name:like]": "%On Call%",
                "filter[book_id:eq]": "7",
                "filter[chapter_id:eq]": "11",
            },
        )
        self.assertEqual(result, {"data": []})

    def test_find_helpers_reject_invalid_match_values(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with self.assertRaisesRegex(ValueError, "match must be one of: exact, like"):
            client.find_books("Operations", match="prefix")

        with self.assertRaisesRegex(ValueError, "match must be one of: exact, like"):
            client.find_pages("On Call", match="prefix")

    def test_search_pages_rejects_non_object_results(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": ["not-an-object"]}):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client.search_pages("ops")

    def test_search_content_filters_by_types_and_preserves_total(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(
            BookStackClient,
            "_request",
            return_value={
                "data": [
                    {"id": 1, "type": "page", "name": "Runbook"},
                    {"id": 2, "type": "book", "name": "Operations"},
                    {"id": 3, "type": "bookshelf", "name": "Engineering"},
                ],
                "total": 9,
            },
        ):
            result = client.search_content("ops", types=["book", "bookshelf"])

        self.assertEqual(
            result,
            {
                "data": [
                    {"id": 2, "type": "book", "name": "Operations"},
                    {"id": 3, "type": "bookshelf", "name": "Engineering"},
                ],
                "total": 9,
            },
        )

    def test_create_page_404_uses_book_or_chapter_specific_not_found(self):
        client = BookStackClient("https://example.test", "id", "secret")

        cases = [
            ({"title": "T", "markdown": "M", "book_id": "7"}, BookNotFoundError, "Book not found"),
            ({"title": "T", "markdown": "M", "chapter_id": "11"}, ChapterNotFoundError, "Chapter not found"),
        ]

        for kwargs, error_type, message in cases:
            with self.subTest(message=message):
                fake_session = FakeSession(FakeResponse(404, content=b"{}"))
                with patch("bookstack_client.requests.Session", return_value=fake_session):
                    with self.assertRaisesRegex(error_type, message):
                        client.create_page(**kwargs)

    def test_create_and_update_resource_methods_use_expected_request_shape(self):
        client = BookStackClient("https://example.test", "id", "secret")

        cases = [
            (
                client.create_book,
                [],
                {"name": "Operations", "description": "Docs", "description_html": "<p>Docs</p>", "tags": [{"name": "env", "value": "prod"}]},
                ("POST", "books"),
                {
                    "json": {
                        "name": "Operations",
                        "description": "Docs",
                        "description_html": "<p>Docs</p>",
                        "tags": [{"name": "env", "value": "prod"}],
                    }
                },
            ),
            (
                client.update_book,
                ["7"],
                {"name": "Operations v2", "tags": []},
                ("PUT", "books/7"),
                {"json": {"name": "Operations v2", "tags": []}, "not_found_error": BookNotFoundError, "not_found_message": "Book not found"},
            ),
            (
                client.create_chapter,
                [],
                {"book_id": "7", "name": "Planning", "description": "Desc", "description_html": "<p>Desc</p>", "tags": [{"name": "topic", "value": "plan"}], "priority": 10},
                ("POST", "chapters"),
                {
                    "json": {
                        "book_id": "7",
                        "name": "Planning",
                        "description": "Desc",
                        "description_html": "<p>Desc</p>",
                        "tags": [{"name": "topic", "value": "plan"}],
                        "priority": 10,
                    },
                    "not_found_error": BookNotFoundError,
                    "not_found_message": "Book not found",
                },
            ),
            (
                client.update_chapter,
                ["11"],
                {"book_id": "8", "name": "Research", "priority": 20},
                ("PUT", "chapters/11"),
                {
                    "json": {"book_id": "8", "name": "Research", "priority": 20},
                    "not_found_error": ChapterNotFoundError,
                    "not_found_message": "Chapter not found",
                },
            ),
            (
                client.create_shelf,
                [],
                {"name": "Publishing", "description": "Desc", "description_html": "<p>Desc</p>", "books": [1, 2], "tags": [{"name": "kind", "value": "published"}]},
                ("POST", "shelves"),
                {
                    "json": {
                        "name": "Publishing",
                        "description": "Desc",
                        "description_html": "<p>Desc</p>",
                        "books": [1, 2],
                        "tags": [{"name": "kind", "value": "published"}],
                    }
                },
            ),
            (
                client.update_shelf,
                ["13"],
                {"name": "Publishing v2", "books": [2, 1]},
                ("PUT", "shelves/13"),
                {
                    "json": {"name": "Publishing v2", "books": [2, 1]},
                    "not_found_error": ShelfNotFoundError,
                    "not_found_message": "Shelf not found",
                },
            ),
        ]

        for method, args, kwargs, expected_call_args, expected_call_kwargs in cases:
            with self.subTest(method=method.__name__):
                with patch.object(BookStackClient, "_request", return_value={"id": 1}) as request:
                    result = method(*args, **kwargs)

                request.assert_called_once_with(*expected_call_args, **expected_call_kwargs)
                self.assertEqual(result, {"id": 1})

    def test_tag_discovery_methods_use_expected_paths_and_params(self):
        client = BookStackClient("https://example.test", "id", "secret")

        with patch.object(BookStackClient, "_request", return_value={"data": [], "total": 0}) as request:
            names = client.list_tag_names(count=100, offset=200)
            values = client.list_tag_values("doc_id", count=50, offset=10)

        self.assertEqual(names, {"data": [], "total": 0})
        self.assertEqual(values, {"data": [], "total": 0})
        self.assertEqual(
            request.call_args_list,
            [
                unittest.mock.call("GET", "tags/names", params={"count": 100, "offset": 200}),
                unittest.mock.call("GET", "tags/values-for-name", params={"name": "doc_id", "count": 50, "offset": 10}),
            ],
        )

    def test_build_resource_payload_helpers_omit_none_fields(self):
        self.assertEqual(
            BookStackClient._build_book_payload(name="Operations", description=None, description_html=None, tags=[]),
            {"name": "Operations", "tags": []},
        )
        self.assertEqual(
            BookStackClient._build_chapter_payload(book_id="7", name="Plan", description=None, description_html=None, tags=None, priority=None),
            {"book_id": "7", "name": "Plan"},
        )
        self.assertEqual(
            BookStackClient._build_shelf_payload(name="Shelf", description=None, description_html=None, books=None, tags=None),
            {"name": "Shelf"},
        )

    def test_request_rejects_invalid_json(self):
        response = FakeResponse(200, content=b"not-json", json_error=ValueError("bad json"))
        fake_session = FakeSession(response)
        client = BookStackClient("https://example.test", "id", "secret")

        with patch("bookstack_client.requests.Session", return_value=fake_session):
            with self.assertRaisesRegex(InvalidResponseError, "Invalid BookStack response"):
                client._request("GET", "system")

    def test_build_page_payload_maps_supported_fields(self):
        payload = BookStackClient._build_page_payload(
            title="Ops Runbook",
            markdown="# Runbook",
            tags=["ops", "runbook"],
            book_id="7",
            chapter_id="11",
        )

        self.assertEqual(
            payload,
            {
                "name": "Ops Runbook",
                "markdown": "# Runbook",
                "tags": ["ops", "runbook"],
                "book_id": "7",
                "chapter_id": "11",
            },
        )

    def test_build_page_payload_omits_none_fields(self):
        payload = BookStackClient._build_page_payload(
            title="Ops Runbook",
            markdown=None,
            tags=None,
            book_id="7",
            chapter_id=None,
        )

        self.assertEqual(
            payload,
            {
                "name": "Ops Runbook",
                "book_id": "7",
            },
        )


if __name__ == "__main__":
    unittest.main()
