# BookStack

这是一个面向 Dify 的 BookStack 插件项目，目标是让 BookStack 成为 Dify 的开源源文档承载平台。

## 项目定位

本项目聚焦于 BookStack 与 Dify 的连接层，优先实现稳定、简单、可维护的 Tool 插件能力，后续再扩展 Datasource 插件。

## 使用场景

- Dify Workflow 生成文档初稿后，发布到 BookStack。
- Dify Agent 或 Chatflow 读取 BookStack 页面进行问答。
- 后续将 BookStack 页面同步到 Dify Knowledge Pipeline。

## 插件能力

当前仓库处于早期阶段，已经完成：

- 仓库骨架
- 架构说明
- 路线图
- API 映射文档
- Issue 拆分
- 最小 `BookStackClient` 占位实现
- 最小 `validate_credentials` 占位实现

后续计划实现：

- 页面搜索、读取、创建、更新、发布
- Book、Chapter 列表能力
- Datasource 同步能力

## 开发路线图

详见 `docs/ROADMAP.md`。

## 本地开发说明

当前仓库没有依赖 Dify CLI 生成骨架，而是根据官方文档手工建立最小结构。后续可使用 `dify plugin package` 进行打包验证。

## 后续计划

优先完成 Tool 插件 MVP，然后补充增强工具与 Datasource 设计。
