# 配置

## Provider 凭据

仅通过 Dify provider 表单配置凭据。

- `base_url`：你的 BookStack 基础 URL
- `token_id`：BookStack API token ID
- `token_secret`：BookStack API token secret

## 凭据指引

- 如果可能，尽量先使用非生产环境的 BookStack 目标进行早期验证。
- 不要在代码、文档示例或测试中硬编码凭据。
- 不要在日志或截图中分享 `token_secret`。

## 建议的首次检查

保存凭据后，在尝试可写工具之前先运行 `validate_credentials`。
