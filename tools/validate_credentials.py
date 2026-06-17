from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from bookstack_client import BookStackClient, BookStackError


class ValidateCredentialsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            client = BookStackClient.from_credentials(self.runtime.credentials)
            client.validate_credentials()
        except BookStackError as exc:
            yield self.create_text_message(f"success=false\nerror={exc}")
            return

        yield self.create_json_message({"success": True})
