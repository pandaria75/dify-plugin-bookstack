# Marketplace 指南

## 当前目标

近期目标是让这个插件更容易在本地完成打包、导入和验证。Marketplace 提交仍然是后续发布步骤，需要等 Tool 插件 MVP 稳定后并重新检查提交要求再进行。

## 当前仓库事实

- `manifest.yaml` 已存在，并且当前声明 `plugin_type: tool`。
- `manifest.yaml` 当前使用 `_assets/icon.svg`，并注册 `provider/bookstack.yaml`。
- `README.md` 为纯英文。
- `PRIVACY.md` 已存在，并记录当前的凭据和数据处理立场。
- 面向用户的文档当前通过 `README.md` 加上 `docs/user/` 进行导流，而实现与规划上下文位于 `docs/developer/` 和 `docs/project/` 下。
- 本仓库记录了打包与导入指引，但尚未记录成功的本地打包或 Dify 冒烟测试证据。
- 在根据已安装的 Dify CLI 进行确认之前，应将这里所有 CLI 命令示例视为与版本相关的工作假设。

## 发布检查清单

在准备任何发布制品或 Marketplace 提交之前，请完成以下清单。

### 1. Manifest 预检

- 确认 `manifest.yaml` 位于仓库根目录。
- 确认 `type: plugin` 与 `plugin_type: tool` 仍与仓库当前范围一致。
- 确认顶层 `version` 与 `meta.version` 都已为预期发布一并更新。
- 确认 `icon: _assets/icon.svg` 仍指向已提交的 SVG 资源。
- 确认 `plugins.tools` 仍引用 `provider/bookstack.yaml`。
- 确认 `supported_dify_version` 与 `minimum_dify_version` 仍符合该发布的预期兼容性声明。

### 2. README 与隐私检查

- 确认 `README.md` 仍为纯英文。
- 确认 `README.md` 只描述已实现工具，并明确将后续工作标记为计划中。
- 确认来自 `README.md` 的链接仍指向当前的 `docs/user/` 指引。
- 确认安装指引仍引导用户使用本地打包与导入流程，而不是指向一个已完成的 Marketplace 列表页。
- 确认 `PRIVACY.md` 仍与实际插件行为一致，且不会暗示超出 Dify 运行时加上已配置 BookStack 实例之外的数据共享。
- 如果面向 Marketplace 的行为或披露发生变化，请在继续发布工作前同时更新 `README.md` 与 `PRIVACY.md`。

### 3. Provider 与资源检查

- 确认 `_assets/icon.svg` 存在，并且与 `manifest.yaml` 引用的是同一个资源。
- 确认 `provider/bookstack.yaml` 仍对工具 YAML 文件使用仓库相对引用。
- 确认 `provider/bookstack.yaml` 仍将 `extra.python.source` 指向 `provider/bookstack.py`。
- 确认 provider 凭据仍仅通过 schema 字段定义，不包含硬编码 URL 或密钥。

### 4. 版本与变更说明

- 在打包前选择下一个发布版本。
- 同时更新两个 manifest 版本字段。
- 准备简短的发布说明，概述已实现工具、重要修复以及任何已知限制。
- 不要将可选的本地验证描述为 Marketplace 认证或生产证据。

### 5. 打包准备

- 在仓库根目录执行操作。
- 使用 `dify --help` 和 `dify plugin --help` 验证当前 CLI 形态。
- 确认仓库树仍符合本仓库当前使用的 Dify 插件布局。
- 在打包前运行下方列出的轻量级仓库验证步骤。

### 6. 本地打包

当前预期命令形式：

```bash
dify plugin package
```

如果已安装的 CLI 报告了不同的语法、参数或输出行为，请遵循当前 CLI help 输出，然后在确认新流程后更新本文档。

预期结果：

- 生成一个用于导入测试的本地 `.difypkg` 制品。

### 7. 导入与冒烟检查

包创建完成后：

1. 打开一个支持插件导入的 Dify 环境。
2. 导入生成的 `.difypkg`。
3. 确认 BookStack 插件出现在插件列表中。
4. 打开 provider 配置表单并验证预期字段会渲染出来。
5. 仅通过 Dify UI 输入非生产环境的 BookStack 凭据。
6. 先运行最小且安全的检查。

建议的最小验证顺序：

1. 导入成功，且没有包结构错误。
2. Provider 表单渲染 `base_url`、`token_id`、`token_secret` 以及可选默认值。
3. 保存测试凭据成功，或返回已记录的面向用户验证错误，且不会泄露密钥。
4. `validate_credentials` 能够针对一个已知可用的非生产 BookStack 目标成功执行。
5. `list_books` 返回可访问的图书。
6. `list_chapters` 返回章节数据，并可选择按 `book_id` 过滤。

对于安全测试目标的可选补充检查：

1. `search_pages`
2. `create_page`
3. `update_page`
4. `publish_page`

基于本地 Docker 的 Dify 验证可以作为补充性的手动路径，但它不是 GitHub Actions 的必需项，也不应被描述为必需的发布证据。

### 8. 发布制品流程

如果打包和导入检查成功：

1. 使用仓库的常规发布流程创建或准备发布标签。
2. 如果这是所选分发流程的一部分，则附加经过验证的 `.difypkg` 制品。
3. 发布包含版本与范围的简洁发布说明。
4. 保持任何附加制品与用于构建它的 manifest 版本一致。

### 9. Marketplace 提交流程

在发起任何 Marketplace 提交或 PR 之前：

1. 重新阅读当前的 Marketplace 提交要求。
2. 再次确认 README、隐私、图标和 manifest 的准确性。
3. 再次确认打包后的插件可以在真实 Dify 环境中成功导入。
4. 再次确认至少最小冒烟路径已经执行，并被记录在某个持久位置。
5. 仅在插件对外部使用足够稳定时才准备 Marketplace 提交。

## 仓库验证命令

这些检查仅针对仓库本地，并且可以在打包前安全运行：

```bash
python3 -m unittest discover -s tests
python3 -m compileall provider tools tests
```

可选的打包检查：

```bash
dify plugin package
```

当本地未安装 Dify CLI，或者当前环境中命令形式尚未确认时，请将打包检查标记为 `NOT_RUN`。

## 证据说明

- 本仓库当前并不声称已记录成功的本地 Dify 打包构建证据。
- 本仓库当前并不声称已记录成功的 Dify 导入冒烟测试证据。
- 本仓库当前并不声称已经完成官方 Marketplace 提交、批准或发布。
- 在任何公开提交之前，请根据当前 Dify 文档重新验证发布流程，因为 Marketplace 与 CLI 要求可能发生变化。
