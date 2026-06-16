# 003. Add BookStack credential schema and provider validation

- **Priority:** P0
- **Type:** Provider

## Background

BookStack access must be driven entirely by Dify credentials.

## Goal

Define the provider credential fields and add validation logic that checks API access safely.

## Implementation Suggestion

- Add `base_url`, `token_id`, and `token_secret`.
- Add optional defaults for `book`, `chapter`, timeout, and SSL verification.
- Validate credentials through a lightweight API call.

## Acceptance Criteria

- Credentials are configurable in the plugin provider.
- Validation returns a readable error on failure.

## Risk

Credential validation must not leak secrets in logs or error messages.
