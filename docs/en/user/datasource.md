# Datasource Status

## Current Position

This repository is still Tool-first.

A separate `bookstack_datasource/` package now exists for Dify Datasource usage, but it should be treated as a separate package track rather than the primary user-facing plugin path.

## Implemented Datasource Scopes

- Page sync by `page_id`
- Chapter sync by `chapter_id`
- Book sync by `book_id`

## Current Caveats

- Release-readiness for the Datasource package is still a follow-up item.
- Installed-runtime content smoke for the broader Datasource package still needs follow-up validation.
- Later sync scopes such as Shelf or full-site sync remain planned work.
