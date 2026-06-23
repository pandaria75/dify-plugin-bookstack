# 项目路线图

## 建议的开发顺序

1. Phase 0：项目初始化与研究。
2. Phase 1：Tool 插件 MVP 基础与核心工具。
3. Phase 2：增强的 Tool 覆盖与更安全的匹配行为。
4. Phase 3：独立的 Datasource 包与后续同步范围。
5. Phase 4：Marketplace 就绪。

## 当前状态摘要

### Phase 1：Tool 插件 MVP

已实现：

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`

### Phase 2：增强的 Tool 覆盖

已实现：

- `list_shelves`
- `list_pages`
- 确定性的标签映射
- 通过标题、路径与 `doc_id` 实现更安全的 `publish_page` 匹配

### Phase 3：Datasource 包

目前已实现：

- 独立的 `bookstack_datasource/` 包
- 页面、章节和图书的 Datasource 范围
- 稳定的元数据映射
- 确定性的共享客户端同步/检查工作流

仍待完成：

- 在 Dify 中进行更广泛的已安装运行时内容冒烟验证
- 后续同步范围，如 Shelf 或全站同步

### Phase 4：Marketplace 就绪

计划中：

- 对齐面向 Marketplace 的文档
- 保持隐私与打包指引为最新状态
- 在发布前记录打包、导入与冒烟检查证据
