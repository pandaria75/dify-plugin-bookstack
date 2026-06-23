# BookStack Plugin for Dify

这是一个面向 Dify 的 BookStack 插件项目，当前以 Tool 插件为主，用于连接 BookStack 并执行凭证校验、页面读取、页面发布及相关列表查询操作。

## 当前已实现能力

当前已实现的 Dify Tool 插件能力：

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`
- `list_shelves`
- `list_pages`

当前仓库方向：

- 以 Tool 插件为先
- 仓库内已存在独立的 Datasource 包路线，但不是当前主要的 Marketplace 面向路径
- 更大范围的 Datasource 能力仍属于后续计划

## 安装与配置

1. 从本仓库构建或获取插件包。
2. 将插件导入支持插件安装的 Dify 环境。
3. 在 Dify 中打开 BookStack provider 配置。
4. 在 Dify 界面中填写 `base_url`、`token_id`、`token_secret`。

相关文档：

- [安装说明](../docs/zh/user/installation.md)
- [配置说明](../docs/zh/user/configuration.md)

## 使用

推荐的首次使用流程：

1. 保存 provider 凭证。
2. 先运行 `validate_credentials`。
3. 再按需使用页面工具与列表工具。

更多说明：

- [工具列表](../docs/zh/user/tools.md)
- [使用示例](../docs/zh/user/examples.md)
- [故障排查](../docs/zh/user/troubleshooting.md)
- [Datasource 状态](../docs/zh/user/datasource.md)

## 隐私

插件使用用户提供的凭证，并且只通过 Dify 运行时连接到用户配置的 BookStack 实例。

详见完整的[隐私政策](../PRIVACY.md)。

## 仓库与支持

- 仓库：<https://github.com/pandaria75/dify-plugin-bookstack>
- 问题反馈：<https://github.com/pandaria75/dify-plugin-bookstack/issues>
- English README: [../README.md](../README.md)
- 开发文档： [../docs/zh/developer/development.md](../docs/zh/developer/development.md)

## 许可证

MIT，详见 [../LICENSE](../LICENSE)。
