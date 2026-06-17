from __future__ import annotations

import importlib.util
import unittest
from unittest.mock import patch

from bookstack_client import PermissionDeniedError


HAS_DIFY_PLUGIN = importlib.util.find_spec("dify_plugin") is not None

if HAS_DIFY_PLUGIN:
    from dify_plugin.errors.tool import ToolProviderCredentialValidationError
    from provider.bookstack import BookStackProvider


@unittest.skipUnless(HAS_DIFY_PLUGIN, "dify_plugin is not installed")
class BookStackProviderTestCase(unittest.TestCase):
    def test_validate_credentials_wraps_bookstack_error_message(self):
        provider = BookStackProvider()
        credentials = {
            "base_url": "https://example.test",
            "token_id": "id",
            "token_secret": "secret",
        }

        with patch("provider.bookstack.BookStackClient.from_credentials") as from_credentials:
            from_credentials.return_value.validate_credentials.side_effect = PermissionDeniedError("Permission denied")

            with self.assertRaisesRegex(ToolProviderCredentialValidationError, "Permission denied"):
                provider._validate_credentials(credentials)


if __name__ == "__main__":
    unittest.main()
