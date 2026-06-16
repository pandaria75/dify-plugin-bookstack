from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from bookstack_client import BookStackClient, BookStackError


class BookStackProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        client = BookStackClient.from_credentials(credentials)
        try:
            client.validate_credentials()
        except BookStackError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc
