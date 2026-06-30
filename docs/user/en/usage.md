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
4. Look for the BookStack plugin in the plugin list.
5. Open the BookStack provider settings.

### Import Screenshots

Use these screens to find the import entry and recognize what the imported plugin view should look like in Dify.

![Dify plugin import entry](../images/dify-plugin-import-entry.png)

*Use this screen to locate the plugin import entry before selecting the plugin package.*

![Imported BookStack plugin view](../images/imported-bookstack-plugin-view.png)

*After import, the plugin list will look similar to this BookStack plugin view.*

## Configure Provider Credentials

Enter credentials through the Dify provider form only:

- `base_url`: your BookStack base URL
- `token_id`: BookStack API token ID
- `token_secret`: BookStack API token secret

Recommended first steps after saving credentials:

1. Save the provider configuration.
2. Run `validate_credentials` first.
3. Only then try read or write tools.

### Credential Safety

- Do not hardcode credentials in code, docs examples, or tests.
- Do not share `token_secret` in logs, screenshots, or tickets.
- Do not share raw `Authorization` headers.
- Prefer a demo or non-production BookStack environment for early validation.
- If a screenshot shows filled values, replace them with fake placeholders before capture.

### Provider Configuration Screenshot

![Dify provider configuration form showing base_url, token_id, and token_secret with redacted or fake sample values](../images/dify-provider-configuration-form.png)

*Provider credential form with redacted or fake sample values only.*

## Available Tool Behavior

### Implemented tools

- `validate_credentials`
- `search_pages`
- `search_content`
- `get_page`
- `export_page_markdown`
- `export_chapter_markdown`
- `export_book_markdown`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `find_books`
- `get_book`
- `create_book`
- `update_book`
- `list_chapters`
- `find_chapters`
- `get_chapter`
- `create_chapter`
- `update_chapter`
- `list_shelves`
- `find_shelves`
- `get_shelf`
- `create_shelf`
- `update_shelf`
- `list_pages`
- `find_pages`
- `list_tag_names`
- `list_tag_values`

### Important usage notes

- The plugin provides BookStack foundation capabilities inside Dify; workflow-specific business composition belongs to your own workflow or adapter layer.
- `search_pages` remains the page-focused search tool.
- `search_content` is the broader global search tool and can filter across supported content types.
- `find_books`, `find_chapters`, `find_pages`, and `find_shelves` are structured name-based lookup tools with `match=like|exact`.
- `get_book`, `get_chapter`, and `get_shelf` read one resource by ID.
- `create_book`, `create_chapter`, `create_shelf`, `update_book`, `update_chapter`, and `update_shelf` add non-delete CRUD coverage for those resources.
- `list_books`, `list_chapters`, `list_shelves`, and `list_pages` are support tools for locating destinations and content.
- Those four `list_*` tools also support optional bounded `sort` (`+field`, `-field`, or `field`) and JSON `filters` using approved resource-specific fields and `eq` / `like` operators.
- `list_tag_names` and `list_tag_values` are discovery-only tag helpers; they do not create, update, or delete tags.
- `list_pages` also supports optional `book_id` and `chapter_id` filtering.
- `export_page_markdown` returns page Markdown for export-oriented workflows.
- `export_chapter_markdown` returns chapter-level aggregate Markdown plus a structured `pages` list with per-page Markdown payloads in chapter order.
- `export_book_markdown` returns book-level aggregate Markdown plus a structured `pages` list with per-page Markdown payloads in BookStack contents traversal order.
- `publish_page` supports create-or-update behavior after you choose or confirm the destination with search, find, or list tools.
- Delete or archive operations are not part of the current plugin scope.
- Do not describe unlisted or planned tools as available.
- Planned follow-up evaluation items from issues #45-#48 remain planning-only and are not implemented tools.

## Recommended First Use Flow

1. Import the plugin into Dify.
2. Configure `base_url`, `token_id`, and `token_secret`.
3. Run `validate_credentials`.
4. Use `find_books`, `find_chapters`, `find_shelves`, `get_book`, `get_chapter`, `get_shelf`, or the list tools to find and inspect destinations you can work with.
5. Use `search_pages`, `search_content`, `get_page`, `export_page_markdown`, `export_chapter_markdown`, `export_book_markdown`, `list_tag_names`, or `list_tag_values` when you need to inspect existing content or export Markdown.
6. Use `create_book`, `update_book`, `create_chapter`, `update_chapter`, `create_shelf`, `update_shelf`, `create_page`, `update_page`, or `publish_page` only after choosing the destination.

For destination discovery, prefer `find_*` when you know the name pattern, `list_*` when you want browsable resource lists with optional bounded sort/filter support, `search_pages` for page-only search, and `search_content` for broader cross-type search.

This order keeps the current Tool-first workflow simple: install, connect, validate, inspect targets, then write content.

## Basic Workflow Example: Publish A Page

The most practical end-to-end example today is based on `publish_page`.

Use this workflow when you want to:

- draft Markdown in Dify
- let a human review the content and destination
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

- Check the final `title`.
- Review the Markdown body before publishing.
- Verify `page_id` when updating a known page.
- Make sure `book_id` and `chapter_id` point to the intended destination.
- Decide whether the workflow should publish now.

### Workflow Screenshots

![Workflow canvas overview with publish_page flow](../images/workflow-canvas-publish-page-flow.png)

*Use this canvas layout as a reference for where `publish_page` fits in the workflow.*

![BookStack successfully generated the page](../images/bookstack-generated-page.png)

*After the tool runs, the resulting BookStack page will look similar to this example.*

## Troubleshooting

### Exact user-facing errors to expect

- `Invalid credentials`
- `Permission denied`
- `Book not found`
- `Chapter not found`
- `Shelf not found`
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

When using `create_book`, `update_book`, `create_chapter`, `update_chapter`, `create_shelf`, `update_shelf`, `create_page`, `update_page`, or `publish_page`, verify the target identifiers and intended destination before retrying.

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
- The plugin may read BookStack books, chapters, shelves, and pages, and may create or update supported books, chapters, shelves, and pages according to the tools you invoke.
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
