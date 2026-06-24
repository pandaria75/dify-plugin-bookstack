# BookStack Dify Plugin Usage

## Scope And Current Position

This repository currently focuses on the BookStack **Tool** plugin for Dify.

- Use the Tool plugin as the main path today.
- A separate Datasource package also exists, but it is a separate package track rather than the primary user path.
- Do not treat later Datasource expansion as part of the current Tool-plugin workflow.

## Before You Start

You need:

- a Dify environment that supports plugin import
- a reachable BookStack instance
- BookStack API credentials created in BookStack

Use placeholders such as `<your-bookstack-host>` in local notes, screenshots, and examples. Do not paste real production URLs, tokens, secrets, or raw `Authorization` headers into docs or shared screenshots.

## Install And Import The Plugin

1. Build or obtain the BookStack plugin package from this repository.
2. Open the plugin management area in Dify.
3. Import the plugin package.
4. Confirm the BookStack plugin appears in the plugin list.
5. Open the BookStack provider settings.

### Screenshot Placeholders For Import

Do not add real screenshots in this first documentation pass. Use text placeholders only.

1. `[Screenshot placeholder: Dify plugin import entry]`
   - Capture the plugin-management page before selecting the package file.
   - Redact workspace names, user names, and production identifiers.
2. `[Screenshot placeholder: imported BookStack plugin view]`
   - Capture the imported plugin card or detail view.
   - Show only the plugin name and visible installation status.

## Configure Provider Credentials

Enter credentials through the Dify provider form only:

- `base_url`: your BookStack base URL
- `token_id`: BookStack API token ID
- `token_secret`: BookStack API token secret

Recommended first check after saving credentials:

1. Save the provider configuration.
2. Run `validate_credentials` first.
3. Only then try read or write tools.

### Credential Safety

- Do not hardcode credentials in code, docs examples, or tests.
- Do not share `token_secret` in logs, screenshots, or tickets.
- Do not share raw `Authorization` headers.
- Prefer a demo or non-production BookStack environment for early validation.
- If a screenshot shows filled values, replace them with fake placeholders before capture.

### Screenshot Placeholder For Provider Setup

`[Screenshot placeholder: Dify provider configuration form showing base_url, token_id, and token_secret with redacted or fake sample values]`

Capture only the provider form state. Do not expose real `token_id`, real `token_secret`, production-only hosts, or hidden credentials that become visible in the UI.

## Available Tool Behavior

### Implemented tools

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`
- `list_shelves`
- `list_pages`

### Important usage notes

- `publish_page` supports create-or-update behavior.
- `list_books`, `list_chapters`, `list_shelves`, and `list_pages` are support tools for locating destinations and content.
- Delete or archive operations are not part of the current plugin scope.
- Do not describe unlisted or planned tools as available.

## Recommended First Use Flow

1. Import the plugin into Dify.
2. Configure `base_url`, `token_id`, and `token_secret`.
3. Run `validate_credentials`.
4. Use `list_books` and `list_chapters` to confirm accessible destinations.
5. Use `search_pages` or `get_page` when you need to inspect existing content.
6. Use `create_page`, `update_page`, or `publish_page` only after confirming the destination.

## Basic Workflow Example: Publish A Page

The most practical end-to-end example today is based on `publish_page`.

Use this workflow when you want to:

- draft Markdown in Dify
- let a human confirm the content and destination
- then create or update a BookStack page

### Suggested node order

1. Start or trigger node
2. Draft generation or upstream content node
3. Structured field mapping
4. Human review or approval step
5. `publish_page` tool node
6. Success or failure routing

### Practical input shape

```json
{
  "title": "Scheduler Design",
  "markdown": "# Scheduler Design\n\nApproved content...",
  "book_id": 1,
  "chapter_id": 12,
  "page_id": null,
  "tags": []
}
```

### Practical success shape

```json
{
  "success": true,
  "action": "created_or_updated",
  "page_id": 123,
  "title": "Scheduler Design",
  "url": "https://<your-bookstack-host>/books/example/page/scheduler-design"
}
```

### `publish_page` behavior summary

1. If `page_id` is provided, the tool updates that page directly.
2. If `page_id` is not provided, the tool searches by exact title matching.
3. It narrows matches further with `book_id` and `chapter_id` when provided.
4. If one exact match remains, it updates that page.
5. If multiple exact matches remain, handle the ambiguity before retrying.
6. If no exact match remains, the tool creates a new page.

Prefer `page_id` whenever your workflow already knows the stable target page.

### Human review checklist

- Confirm the final `title`.
- Confirm the Markdown body is ready.
- Confirm `page_id` when updating a known page.
- Confirm `book_id` and `chapter_id` point to the intended destination.
- Confirm the workflow should publish now.

### Screenshot Placeholders For Workflow Docs

- `[Screenshot placeholder: workflow canvas overview with publish_page flow]`
- `[Screenshot placeholder: human review step with sample content only]`
- `[Screenshot placeholder: publish_page tool configuration with placeholder values only]`
- `[Screenshot placeholder: success branch showing sample page_id, title, url, and action]`

When preparing screenshots later, redact usernames, internal project names, sensitive page URLs, workspace names, and any production identifiers.

## Troubleshooting

### Exact user-facing errors to expect

- `Invalid credentials`
- `Permission denied`
- `Book not found`
- `Chapter not found`
- `Page not found`
- `BookStack API unavailable`
- `Invalid BookStack response`

### Recommended triage order

1. Recheck `base_url`, `token_id`, and `token_secret` in Dify.
2. Run `validate_credentials`.
3. Confirm the BookStack account can access the target content.
4. Recheck target `book_id`, `chapter_id`, or `page_id`.
5. Retry later if the BookStack API is temporarily unavailable.

### Write-tool caution

When using `create_page`, `update_page`, or `publish_page`, verify the target book, chapter, or page identifiers before retrying.

## Datasource Status

If you are evaluating Datasource support, keep these expectations in mind:

- this repository is still Tool-first
- a separate `bookstack_datasource/` package exists
- Datasource usage follows a separate package path, not the main Tool-plugin flow
- broader Datasource rollout and release-readiness are still follow-up work

The currently documented Datasource path is focused on syncing BookStack content by an explicit target identifier, such as:

- a page by `page_id`
- a chapter by `chapter_id`
- a book by `book_id`

## Privacy And Redaction Notes

- This plugin connects only to the BookStack instance configured by the user.
- The plugin may read, create, and update BookStack pages, books, and chapters according to the tools you invoke.
- The plugin uses API credentials supplied through Dify plugin credential settings.
- No content is intended to be sent to any third party beyond the configured BookStack instance and the Dify runtime that executes the plugin.
- The plugin does not log `token_secret` values.
- How content is later used by Dify Workflow, Chatflow, Agent, or Knowledge features depends on your own Dify configuration and data-handling choices.

For any future screenshots, use sample data only and redact:

- real BookStack hosts
- real token values
- raw `Authorization` headers
- user names
- internal project names
- production page URLs or identifiers
