# BookStack Datasource 设计草案

> 状态：**Target design / 非当前实现**
>
> 本文描述 BookStack Dify 插件后续可能采用的 Datasource 设计方向，用于支持 Issue `#025` 到 `#028` 的实现规划。
> 当前仓库已实现的是 Tool plugin 能力；**Datasource 运行时行为、插件契约与交付形态尚未在本仓库中实现或验证**。

## 目标与边界

- 目标：为后续 BookStack Datasource MVP 提供紧凑设计基线，覆盖 sync scope、metadata mapping、内容抽取与后续验证计划。
- 当前不做：不新增 Datasource Python/YAML 文件，不改变现有 Tool plugin 行为，不声明 Datasource 已可用。
- 设计优先级：先支持 `Page`、`Chapter`、`Book` 三种 sync scope；`Shelf` 与 full-site sync 作为后续扩展。

## 与现有 Tool plugin 的关系

- 当前插件定位仍是 Tool-first，Datasource 是 Phase 3 的后续扩展方向。
- 未来若 Dify 版本允许，Datasource 应尽量复用现有 provider credentials：`base_url`、`token_id`、`token_secret`。
- 与 BookStack API 的 HTTP 访问应继续复用现有 `BookStackClient` 设计职责，而不是重新分散实现 URL 规范化、认证、超时、SSL、错误映射等逻辑。
- 本设计只定义目标行为与边界，不预设 Datasource 一定与当前 Tool plugin 以同一插件包交付；该点仍需结合 Dify 版本能力验证。

## Dify Datasource plugin 契约假设与未知项

以下内容是**版本敏感假设**，需要在本地 Dify Docker 环境中单独验证后，才能进入实现阶段：

- 假设 Dify 当前部署版本支持独立或兼容的 Datasource plugin contract。
- 假设 Datasource 可在抓取阶段输出文本内容与 metadata，供 Knowledge Pipeline 使用。
- 假设 metadata 支持至少保留字符串、数字、时间戳、标签或可序列化附加字段。
- 假设 Datasource 支持增量同步所需的 source identity 或上次同步依据。

当前未知项：

- 当前本地 Dify 版本的 Datasource plugin 接口、目录结构、manifest 约束是否与 Tool plugin 兼容。
- Datasource 是否必须作为单独插件包发布，而不是与现有 Tool plugin 共存于同一包。
- Knowledge Pipeline 对 metadata 字段名、字段类型、长度限制、保留字的真实要求。
- 对分页拉取、重试、断点续传、删除同步的官方约束。

## Sync Scope 设计

### `Page`

- 输入：单个 `page_id`。
- 行为：读取单页内容与元数据，生成一个最小同步单元。
- 用途：最适合精确导入、手工补录、问题排查。

### `Chapter`

- 输入：`chapter_id`。
- 行为：先读取 Chapter 元数据，再枚举其下属 Pages，按页生成同步单元。
- 用途：适合按文档章节批量导入。

### `Book`

- 输入：`book_id`。
- 行为：读取 Book 元数据，并按 Book 下的 Chapter / Page 结构展开同步。
- 用途：作为 Datasource MVP 的主要批量同步入口。

### 后续扩展：`Shelf`

- 不纳入 MVP。
- 预期行为：按 `shelf_id` 展开多个 Books，再沿用 Book 级同步逻辑。
- 主要风险：同步规模、权限可见性、分页与去重复杂度上升。

### 后续扩展：full-site

- 不纳入 MVP。
- 预期行为：在用户权限范围内遍历站点全部可见内容。
- 主要风险：范围过大、性能压力更高、增量同步与删除检测更复杂。

## Metadata Mapping

建议以 Page 作为最终 ingestion 单元，即使 Chapter 或 Book 作为上层 scope，最终仍输出逐页文档，便于检索、重建来源与增量更新。

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| `source` | 固定值或 BookStack 来源标识 | 标识数据来自 BookStack Datasource |
| `bookstack_page_id` | BookStack Page ID | Page 级唯一来源标识 |
| `bookstack_chapter_id` | BookStack Chapter ID | 若页面属于 Chapter，则填充 |
| `bookstack_book_id` | BookStack Book ID | 页面所属 Book |
| `title` | Page title | 知识条目显示标题 |
| `url` | Page URL | 回跳到 BookStack 原页面 |
| `book_id` | BookStack Book ID | 兼容更通用 metadata 查询场景 |
| `chapter_id` | BookStack Chapter ID | 兼容更通用 metadata 查询场景 |
| `tags` | BookStack tags | 保留原标签语义，具体序列化方式待验证 |
| `created_at` | BookStack created timestamp | 原始创建时间 |
| `updated_at` | BookStack updated timestamp | 原始更新时间，也是候选增量同步依据 |
| `sync_scope` | Datasource 输入范围 | `page` / `chapter` / `book` |
| `sync_source_id` | Datasource 输入 ID | 触发本次同步的 page/chapter/book ID |
| `content_format` | 内容格式标识 | 预期为 `html` 或转换后的 `markdown`，待实现阶段确认 |

补充约束：

- `source` 应稳定且可用于区分未来其他 Datasource。
- IDs 建议同时保留 BookStack 原生命名与通用命名，避免后续 Pipeline 只接受某一套字段时缺少兼容余地。
- `updated_at` 应优先保留源系统时间语义，不在设计阶段引入本地加工时间。

## 内容抽取与格式化策略

- BookStack 页面原始内容更接近 `HTML` 表达，因此 Datasource 首选应保留高保真内容来源。
- 若 Dify Knowledge Pipeline 更偏向纯文本或 `Markdown`，实现阶段可增加受控转换，但不应在设计阶段假设转换结果完全无损。
- 建议保留 `content_format` metadata，以区分直接抓取的 `html` 与后续规范化结果。
- 对 `Chapter` 和 `Book` 范围，不建议把多个页面拼成一个超长文档；应保持逐页输出，减少重同步成本并保留细粒度来源。

## 复用现有 credentials、client、errors 与 pagination 的设计关系

- credentials：未来 Datasource 应复用现有 provider credentials，不新增额外 secret 字段，除非 Dify Datasource contract 明确要求。
- `BookStackClient`：继续作为共享 HTTP wrapper，承接 `/api` 前缀处理、auth header、timeout、SSL、错误映射与响应解析。
- errors：用户可见错误术语应延续现有约定，例如 `Invalid credentials`、`Permission denied`、`Book not found`、`Chapter not found`、`Page not found`、`BookStack API unavailable`、`Invalid BookStack response`。
- pagination：Book、Chapter、Shelf 或 full-site 扩展可能需要遍历分页结果；实现阶段应把分页逻辑集中在共享 client 或 Datasource 适配层，而不是散落在单个 sync scope 分支中。

## 验证计划

本设计文档对应的当前任务仅做文档落地；运行时验证暂不执行。后续进入实现前，建议按以下顺序验证：

1. 验证当前 Dify Docker 版本是否支持目标 Datasource plugin contract。
2. 验证 Datasource 与 Tool plugin 是否可共存，或是否必须拆分插件包。
3. 验证 metadata 字段名、字段类型、标签表达方式、时间字段在 Knowledge Pipeline 中的可接受性。
4. 验证 Book、Chapter、Page 范围下的分页、权限错误与增量更新依据。
5. 验证内容格式在 `html` 与 `markdown` 间的最小可用策略。

## 后续 Issue 映射

- `#025`：实现 BookStack Datasource MVP，优先打通最窄可用同步链路。
- `#026`：补齐 Book 级 sync range 行为。
- `#027`：补齐 Chapter 级 sync range 行为。
- `#028`：细化并稳定 Knowledge Pipeline metadata mapping。

## 非目标与风险

- 非目标：本阶段不定义删除同步、archive、full-site crawler、复杂去重策略。
- 风险：若当前 Dify 版本的 Datasource contract 与预期不同，本文中的交付形态与 metadata 约定都可能需要调整。
- 风险：若 Knowledge Pipeline 对 metadata 结构限制较强，可能需要缩减字段或引入字段映射层。
- 风险：若 BookStack 内容格式转换损失较大，可能需要以 `html` 为主并额外提供简化文本。
