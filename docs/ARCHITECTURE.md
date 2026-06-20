# Architecture

## Dify Plugin Layer

The plugin is structured as a Dify Tool plugin. The provider defines credentials and validation, while tools implement user-facing actions such as page read/write operations.

## BookStackClient Layer

`BookStackClient` is the internal HTTP wrapper around BookStack REST API calls. It normalizes the base URL, adds the `/api` prefix, sets the authorization header, applies timeout and SSL settings, and translates HTTP failures into readable domain errors.

## Tool Implementation Layer

Each tool should stay thin and focus on input validation, request mapping, and response shaping. Shared BookStack behavior belongs in `BookStackClient`.

## Future Datasource Layer

Phase 3 will add a Datasource plugin path that maps BookStack documents into Dify Knowledge Pipeline records with stable metadata.

## Error Handling Strategy

User-facing errors should stay short and actionable:

- `Invalid credentials`
- `Permission denied`
- `Book not found`
- `Chapter not found`
- `Page not found`
- `BookStack API unavailable`
- `Invalid BookStack response`

The shared `BookStackClient` owns status and payload classification for current tools:

- `401` maps to `Invalid credentials`.
- `403` maps to `Permission denied`.
- `404` maps to a method-specific not-found error: `Book not found`, `Chapter not found`, `Page not found`, or internal fallback `Resource not found` only when a caller does not provide a resource-specific override.
- `400` and `422` map to `Invalid BookStack response` for the current implemented methods.
- `429`, network failures, request timeouts, and `5xx` responses map to `BookStack API unavailable`.
- Malformed JSON and non-object JSON payloads map to `Invalid BookStack response`.
- Other unexpected non-success responses fall back to `BookStack API unavailable`.

## Credential Safety Strategy

- Store credentials only in Dify plugin credential settings.
- Never hardcode base URLs, token IDs, or token secrets.
- Never log `token_secret` values.
- Prefer minimal credential validation that does not expose sensitive details.
