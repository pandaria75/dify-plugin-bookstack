# Development Guide

## Local Development

This repository currently uses a manually created plugin skeleton based on the official Dify documentation.

## Recommended Next Steps

1. Keep the implemented Phase 1 core tools stable: `search_pages`, `get_page`, `create_page`, `update_page`, and `publish_page`.
2. Add `list_books` and `list_chapters` as Phase 1 support tools.
3. Expand unit tests for client behavior and payload mapping as tool coverage grows.
4. Validate packaging against a test Dify instance.
5. Expand into Phase 2, then Phase 3, then Marketplace preparation.

## Safety Rules

- Do not hardcode BookStack endpoints.
- Do not hardcode API tokens.
- Do not log secrets.
- Keep behavior minimal until the MVP tools are stable.
