# BookStack

这是一个面向 Dify 的 BookStack 插件项目，目标是让 BookStack 成为 Dify 的开源源文档承载平台。

## 项目定位

本项目聚焦于 BookStack 与 Dify 的连接层，优先实现稳定、简单、可维护的 Tool 插件能力，后续再扩展 Datasource 插件。

## 使用场景

- Dify Workflow 生成文档初稿后，发布到 BookStack。
- Dify Agent 或 Chatflow 读取 BookStack 页面进行问答。
- 后续将 BookStack 页面同步到 Dify Knowledge Pipeline。

## 插件能力

当前仓库仍处于早期阶段，已经完成：

- 仓库骨架
- 架构说明
- 路线图
- API 映射文档
- Issue 拆分
- 共享 `BookStackClient`
- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`
- 独立 Datasource 包中的 Page-only MVP（单个 `page_id`）
- 基础单元测试覆盖（共享客户端与页面参数/载荷映射）

后续计划实现：

- 更丰富的工具增强能力（例如更安全的页面匹配与扩展查询）
- Book / Chapter 等更大范围的 Datasource 同步能力

说明：当前 Datasource 仍是一个范围受限的 MVP，实现位于独立的 `bookstack_datasource/` 包中；真实 SDK import、daemon source-root 检查、基于临时 BookStack 内容的 live Page-only Datasource smoke，以及 Dify UI 中的插件安装均已通过。发布就绪前仍建议在恢复正常签名校验后再做一次验证。

## 开发路线图

详见 `docs/ROADMAP.md`。

## 本地开发说明

当前仓库没有依赖 Dify CLI 生成骨架，而是根据官方文档手工建立最小结构。当前文档将 `dify plugin package` 视为可行的打包命令形态，但由于 CLI 版本可能变化，实际操作前应先用 `dify --help` 与 `dify plugin --help` 进行确认。更多本地打包、导入与验证步骤见 `docs/DEVELOPMENT.md` 与 `docs/MARKETPLACE.md`。

## 后续计划

优先稳定当前已实现的 Phase 1 工具集与 Page-only Datasource MVP，补充更多验证与打包导入证据，然后再推进增强工具与更大范围的 Datasource 同步。
