# Development Guide

## Local Development

This repository currently uses a manually created plugin skeleton based on the official Dify documentation.

## Recommended Next Steps

1. Finish Phase 0 documentation and skeleton review.
2. Implement `BookStackClient` and credential validation.
3. Build the Phase 1 MVP tools in this order: `search_pages`, `get_page`, `create_page`, `update_page`, `publish_page`.
4. Add `list_books` and `list_chapters`.
5. Write unit tests for client behavior and payload mapping.
6. Validate packaging against a test Dify instance.
7. Expand into Phase 2, then Phase 3, then Marketplace preparation.

## Safety Rules

- Do not hardcode BookStack endpoints.
- Do not hardcode API tokens.
- Do not log secrets.
- Keep behavior minimal until the MVP tools are stable.
