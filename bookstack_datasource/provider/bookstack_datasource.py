from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin.interfaces.datasource import DatasourceProvider


class BookStackDatasourceProvider(DatasourceProvider):
    def _validate_credentials(self, credentials: Mapping[str, Any]) -> None:
        required_fields = ("base_url", "token_id", "token_secret")

        missing_fields = [field for field in required_fields if not str(credentials.get(field, "")).strip()]
        if missing_fields:
            raise ToolProviderCredentialValidationError("Invalid credentials")
