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

## Credential Safety Strategy

- Store credentials only in Dify plugin credential settings.
- Never hardcode base URLs, token IDs, or token secrets.
- Never log `token_secret` values.
- Prefer minimal credential validation that does not expose sensitive details.
