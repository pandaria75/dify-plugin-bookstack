# Datasource 状态

## 当前定位

本仓库仍然是 Tool-first。

现在虽然已有一个独立的 `bookstack_datasource/` 包用于 Dify Datasource 用法，但应将其视为独立的包路线，而不是主要的面向用户插件路径。

## 已实现的 Datasource 范围

- 按 `page_id` 同步页面
- 按 `chapter_id` 同步章节
- 按 `book_id` 同步图书

## 当前注意事项

- Datasource 包的发布就绪性仍是后续事项。
- 更广泛的 Datasource 包已安装运行时内容冒烟验证仍需后续补充。
- 之后的同步范围（如 Shelf 或全站同步）仍属于计划中的工作。
