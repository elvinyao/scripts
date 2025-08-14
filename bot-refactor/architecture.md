## 架构说明（Bot + Service 分层）

### 1. 背景概述
- 旧系统：多个独立 Bot 直连外部service APEX/Jira/Confluence/Mattermost/LDAP/，专用service htmltag-service（indication-imp）/aicheck-service(analysis-check) 完成任务处理与结果回写。
- 新系统：由 10 个业务 Bot + 4 个中间件 Service 组成。Bot 每 3 秒轮询 APEX 拉取任务，并每 3 秒回写进度与结果；所有对外系统访问统一经中间件 Service。

### 2. 名词与术语统一
- APEX API：Oracle APEX 暴露的 REST API，用于任务获取与进度/结果回写。
- Bot（业务 Bot）：消费 APEX 任务，编排 Service 完成业务处理。
- Service（中间件 Service）
  - auth-service：用户鉴权与权限校验。
  - ticket-service：封装 Jira 操作（查询/创建/更新/删除、JQL、字段映射、限流、幂等）。
  - wiki-service：封装 Confluence 操作（页面查询/生成/更新、模板、层级）。
  - mattermost-service：统一通知发送。
- Issue Type：Jira 的 `issueType` 名称，不得硬编码，可配置/覆盖。
- FieldName：Jira 的 FieldName，不得硬编码，可配置。
- Excel 模板/文件：Import 任务附带 Excel；Export 任务按筛选条件生成并回传 Excel。
- 轮询与回写：任务轮询间隔 3 秒；进度回写间隔 3 秒（可配置）。

### 3. 总体架构与数据流
1) Bot 定时（3 秒）向 APEX API 拉取待处理任务。  
2) Bot 调用 auth-service 校验用户权限与上下文。  
3) Bot 根据任务类型编排 ticket-service、wiki-service、mattermost-service 完成业务处理。  
4) Bot 将处理进度与结果回写 APEX；Export 将生成的 Excel 上传至 APEX。  

### 4. 中间件 Service 职责边界
- auth-service
  - 输入：用户身份、目标操作/资源
  - 输出：是否有权限及必要上下文（项目、权限范围）
- ticket-service
  - 输入：语义化请求（按条件查询、批量创建/更新/删除）
  - 输出：Jira 数据对象/操作结果
  - 能力：JQL 生成、字段名⇄cfid 映射、IssueType 配置、统一限流、幂等写入
- wiki-service
  - 输入：页面模板、数据、目标空间/层级
  - 输出：页面创建/更新/查询结果
- mattermost-service
  - 输入：频道/用户、消息体
  - 输出：发送结果（带重试与降级）

### 5. 业务 Bot 分类与职责（示例 5 个，其他待补全）
- 批量导入/导出类：`task-imp`、`task-exp`、`case-imp`、`case-exp`、`indication-imp`
- 通知类：`notice-set`、`analysis-set`、`update-set`（待细化）
- 状况把握类：`pr-set`、`qe-set`（待细化）

### 6. 调用关系矩阵
| 业务 Bot | 拉取任务(APEX) | 权限校验(auth) | Jira 操作(ticket) | Confluence(wiki) | 通知(mattermost) | 进度/结果回写(APEX) | LDAP用户获取 | HTMLTAG转换处理Service | AI分析CheckService
|---|---|---|---|---|---|---|---|---|---|
| task-imp | ✅ | ✅ | ✅ 批量增改删 | — | 可选 | ✅ | ✅ (通过auth权限校验获取)| — |
| task-exp | ✅ | ✅ | ✅ 查询 | — | — | ✅（含 Excel 上传） | ✅(通过auth权限校验获取，输出user list单独使用) | — |
| case-imp | ✅ | ✅ | ✅ 批量增改删 | — | — | ✅ | ✅ | ✅ (通过auth权限校验获取)| — |
| case-exp | ✅ | ✅ | ✅ 查询 | — | — | ✅（含 Excel 上传） | ✅ | ✅ (通过auth权限校验获取)| — |
| indication-imp | ✅ | ✅ | ✅ 批量增改删 | ✅ 解析/回写 | 可选 | ✅ | ✅ | ✅ (通过auth权限校验获取)| ✅ |

说明：
- Task 默认 `issueType=Task`，可由程序配置覆盖。  
- Case/Indication：程序配置给出默认；Case 可由 Excel「设置」Sheet 覆盖；Indication 可由 Confluence「设置」表覆盖。

### 7. Service ↔ 外部系统映射
| Service | 外部系统 | 主要能力 | 关键策略 |
|---|---|---|---|
| auth-service | 内部/APEX 上下文 | 鉴权、权限范围解析 | 失败快速返回、可审计 |
| ticket-service | Jira | 查询、批量创建/更新/删除、JQL、字段/IssueType 映射 | 幂等（外部键/去重）、统一限流（错误降速/稳定恢复） |
| wiki-service | Confluence | 页面查询/生成/更新、模板、层级管理 | 模板化与幂等更新（外键/标签识别） |
| mattermost-service | Mattermost | 频道/私聊通知 | 重试与降级（记录不中断主流程） |

### 8. 典型业务流程
- Import（`task-imp`/`case-imp`/`indication-imp`）
| 步骤 | 动作 | 说明 | 主要调用 |
|---|---|---|---|
| 1 | 拉取任务 | 每 3 秒轮询 | APEX API |
| 2 | 权限校验 | 用户/项目权限 | auth-service |
| 3 | 解析输入 | Excel 或 Confluence 页面 | 本地解析 + wiki-service（仅 Indication） |
| 4 | 业务写入 | Jira 批量增改删 | ticket-service |
| 5 | 进度回写 | 过程与结果 | APEX API |
| 6 | 通知（可选） | 推送处理结果 | mattermost-service |

- Export（`task-exp`/`case-exp`）
| 步骤 | 动作 | 说明 | 主要调用 |
|---|---|---|---|
| 1 | 拉取任务 | 每 3 秒轮询 | APEX API |
| 2 | 权限校验 | 用户/项目权限 | auth-service |
| 3 | 数据查询 | 按条件查询 Jira | ticket-service |
| 4 | 生成 Excel | 使用模板渲染 | 本地生成 |
| 5 | 回传结果 | 上传 Excel + 进度 | APEX API |

### 9. 配置与可变项
| 配置项 | 默认值来源 | 任务级覆盖来源 | 备注 |
|---|---|---|---|
| IssueType（Task/Case/Indication 等） | 程序配置 | Excel「设置」Sheet（Case）/Confluence 设置表（Indication） | 禁止硬编码 |
| 字段名映射（含 cfid） | 程序配置 | 按环境覆盖 | 解决不同环境字段差异 |
| Export Excel 模板 | 配置文件 | — | 导出流程使用 |
| Confluence 页面模板 | 配置文件 | — | 供 wiki-service 使用 |
| 轮询/回写间隔 | 3 秒 | 配置可调 | 全局控制 |

### 10. 非功能与运维约束
- 幂等：对外写入可重试不重复（外部键、版本/去重逻辑）。  
- 统一节流：所有 Jira 调用经 ticket-service 动态限流（错误降速、稳定恢复）。  
- 可用性：发布/停机不影响其他 Bot（独立部署、无共享可变状态）。  
- 观测性：统一日志与指标（成功率、QPS、错误分布、限流动作、重试次数）。  

### 11. 设计补充（JQL 与字段）
- JQL 生成位置：由 ticket-service 统一负责，支持模板化与参数化。  
- 自定义字段 cfid：通过“字段名⇄cfid”映射在 ticket-service 内部转译，避免 Bot 层硬编码。  

### 12. 发布约束
- 需求：Release 停机不影响别的 Bot；通过独立部署与灰度/滚动发布达成。