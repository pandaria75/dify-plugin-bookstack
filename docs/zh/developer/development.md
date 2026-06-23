# 开发者开发指南

## 仓库形态

本仓库最初是一个 Dify Tool 插件，现在也包含一个独立的 Datasource 包。Tool 插件仍然是主要重点。

## 本地开发优先事项

1. 保持已实现的 Tool 功能稳定。
2. 将共享客户端行为集中在 `BookStackClient` 中。
3. 在文档中保持“已实现”与“计划中”的准确区分。
4. 将 Datasource 的打包和运行时验证视为独立的包事项。

## Dify CLI 说明

Dify plugin CLI 应被视为与版本相关。

建议的验证命令：

```bash
dify --help
dify plugin --help
```

## 打包假设

- `manifest.yaml` 将根插件声明为 Dify `tool` 插件。
- `provider/bookstack.yaml` 是 provider 入口。
- YAML 与 Python 源引用使用仓库相对路径。

## Datasource 打包说明

- `bookstack_datasource/manifest.yaml` 定义一个独立的 Datasource 包。
- 根目录 `bookstack_client.py` 是规范来源。
- `bookstack_datasource/bookstack_client.py` 是确定性生成的子集。
- 使用 `python3 scripts/sync_bookstack_client.py` 重新生成 Datasource 副本。
- 使用 `python3 scripts/sync_bookstack_client.py --check` 检测漂移。

## 安全规则

- 不要硬编码 BookStack 端点。
- 不要硬编码 API token。
- 不要记录密钥。
- 保持变更最小，并与 Tool-first 的仓库方向一致。
