# 故障排查

## 常见面向用户的错误

- `Invalid credentials`
- `Permission denied`
- `Book not found`
- `Chapter not found`
- `Page not found`
- `BookStack API unavailable`
- `Invalid BookStack response`

## 建议的排查顺序

1. 在 Dify 中重新检查 `base_url`、`token_id` 和 `token_secret`。
2. 运行 `validate_credentials`。
3. 确认 BookStack 账户对目标内容具有访问权限。
4. 如果 BookStack API 暂时不可用，请稍后重试。

## 写入工具注意事项

使用 `create_page`、`update_page` 或 `publish_page` 时，在重试之前请确认目标图书、章节或页面标识符。
