# 开发者架构

## 插件分层

### Dify 插件层

根插件被组织为一个 Dify Tool 插件。provider 定义凭据与验证，而 tools 实现面向用户的操作。

### 共享客户端层

`BookStackClient` 是用于 BookStack API 调用的共享 HTTP 封装。它会规范化基础 URL、应用 `/api` 前缀、设置授权头、应用超时与 SSL 行为，并将失败映射为面向用户的错误。

### 工具实现层

工具应保持轻量，并专注于输入验证、请求映射与响应整形。共享的 BookStack 行为应归属于 `BookStackClient`。

### 独立的 Datasource 包

该仓库还包含一个独立的 `bookstack_datasource/` 包，用于页面、章节和图书同步范围。这仍然是一条区别于主 Tool 插件的独立包路径。

## 错误契约

面向用户的错误应保持简短且稳定：

- `Invalid credentials`
- `Permission denied`
- `Book not found`
- `Chapter not found`
- `Page not found`
- `BookStack API unavailable`
- `Invalid BookStack response`

## 凭据安全

- 仅在 Dify provider schema 中保存凭据。
- 绝不要硬编码 URL、token ID 或 token secret。
- 绝不要记录 `token_secret`。
