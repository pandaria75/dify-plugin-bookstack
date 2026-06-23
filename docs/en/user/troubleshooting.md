# Troubleshooting

## Common User-Facing Errors

- `Invalid credentials`
- `Permission denied`
- `Book not found`
- `Chapter not found`
- `Page not found`
- `BookStack API unavailable`
- `Invalid BookStack response`

## Recommended Triage Order

1. Recheck `base_url`, `token_id`, and `token_secret` in Dify.
2. Run `validate_credentials`.
3. Confirm the BookStack account has access to the target content.
4. Retry later if the BookStack API is temporarily unavailable.

## Write Tool Caution

When using `create_page`, `update_page`, or `publish_page`, verify the target book, chapter, or page identifiers before retrying.
