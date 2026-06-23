# Configuration

## Provider Credentials

Configure credentials through the Dify provider form only.

- `base_url`: your BookStack base URL
- `token_id`: BookStack API token ID
- `token_secret`: BookStack API token secret

## Credential Guidance

- Use a non-production BookStack target for early validation when possible.
- Do not hardcode credentials in code, docs examples, or tests.
- Do not share `token_secret` in logs or screenshots.

## Recommended First Check

After saving credentials, run `validate_credentials` first before trying write-capable tools.
