# 安装

## 范围

本仓库当前主要围绕面向 BookStack 的 Dify Tool 插件。另有一个独立的 Datasource 包存在，但 Tool 插件仍然是主要的用户路径。

## 前置条件

- 一个支持插件导入的 Dify 环境。
- 一个可访问的 BookStack 实例。
- 在 BookStack 中创建好的 API 凭据。

## 当前安装流程

1. 从本仓库构建或获取插件包。
2. 将该插件包导入 Dify。
3. 在 Dify 中打开 BookStack provider 设置。
4. 仅通过 Dify UI 输入凭据。
5. 保存 provider 配置。

## 说明

- Dify CLI 打包细节与版本相关。
- 不要将生产环境密钥粘贴到共享文档、截图或提交中。
- Datasource 的打包与导入遵循独立的包路径，并作为单独能力记录，而不是主 Tool 插件流程。
