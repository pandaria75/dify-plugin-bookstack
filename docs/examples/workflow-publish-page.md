# Example Workflow: Publish Page

This example describes the intended Dify Workflow usage for the future `publish_page` tool.

1. Generate a draft page in a prior node.
2. Route the draft through approval or review logic.
3. Call `publish_page` with title, markdown, and BookStack location data.
4. Store the returned `page_id`, `title`, `url`, and `action`.
