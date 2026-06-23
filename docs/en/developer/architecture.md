# Developer Architecture

## Plugin Layers

### Dify plugin layer

The root plugin is structured as a Dify Tool plugin. The provider defines credentials and validation, while tools implement user-facing operations.

### Shared client layer

`BookStackClient` is the shared HTTP wrapper for BookStack API calls. It normalizes the base URL, applies the `/api` prefix, sets the authorization header, applies timeout and SSL behavior, and maps failures into user-facing errors.

### Tool implementation layer

Tools should stay thin and focus on input validation, request mapping, and response shaping. Shared BookStack behavior belongs in `BookStackClient`.

### Separate Datasource package

The repository also contains a separate `bookstack_datasource/` package for Page, Chapter, and Book sync scopes. This remains a separate package path from the main Tool plugin.

## Error Contract

User-facing errors should remain short and stable:

- `Invalid credentials`
- `Permission denied`
- `Book not found`
- `Chapter not found`
- `Page not found`
- `BookStack API unavailable`
- `Invalid BookStack response`

## Credential Safety

- Keep credentials in the Dify provider schema only.
- Never hardcode URLs, token IDs, or token secrets.
- Never log `token_secret`.
