# 项目决策

## 当前文档目的

该文件记录当前文档形态与插件形态背后的长期项目决策。

## 决策

### 1. Tool-first 仓库方向

该仓库最初首先作为 BookStack Tool 插件启动，因为当下的使用场景是围绕 BookStack 页面操作的工作流自动化。

### 2. Datasource 作为独立包后续跟进

Datasource 支持以独立的 `bookstack_datasource/` 包存在，而不是并入根 Tool 插件包。

### 3. 共享 BookStack 行为归属于 `BookStackClient`

基础 URL 规范化、`/api` 前缀、授权头构建、超时与 SSL 行为，以及面向用户的错误映射，均属于共享客户端层。

### 4. 面向用户的错误术语保持稳定

仓库使用稳定的错误术语，例如 `Invalid credentials`、`Permission denied`、`Book not found`、`Chapter not found`、`Page not found`、`BookStack API unavailable` 和 `Invalid BookStack response`。

### 5. 仓库相对插件路径是本地约定

插件 YAML 引用以及 `extra.python.source` 值使用仓库相对路径。

### 6. Datasource 客户端复用当前采用确定性生成

根目录 `bookstack_client.py` 保持为规范来源，而 Datasource 包使用一个生成的子集以及同步/检查验证，以避免手动漂移。

### 7. 发布就绪性保持保守

Marketplace 与发布工作不应夸大当前能力。项目会将已实现功能记录为已实现，并将计划中的后续工作记录为计划中。
