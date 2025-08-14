一、背景概述
- 背景1（现有旧系统）
  - 10个独立的bot从 Oracle APEX 的 REST API（简称“APEX API”）获取任务，有的任务是包括excel文件的，有的任务是根据api的field的confluence url，去获取confluence page的内容作为输入的。
  - 按任务设置直接调用 Jira、Confluence、Mattermost 完成数据获取、加工与业务处理。
  - 结果回写到 Jira、Confluence，或者输出成Excel；部分场景通过 Mattermost 发送通知。

- 背景2（新系统目标方案）
  - 架构由 10 个业务 Bot + 4 个中间件 Service 构成：
    - 业务 Bot：每 3 秒从 APEX API 拉取任务，调用各 Service 完成业务处理。
    - 中间件 Service：ticket-service（Jira 相关）、wiki-service（Confluence 相关）、mattermost-service（通知）、auth-service（鉴权）。
  - 业务 Bot 在处理期间还需要每 3 秒通过 APEX API 回写用户处理进度。

二、名词与术语统一
- APEX API：Oracle APEX 暴露的 REST API，用于任务获取与结果/进度回写。
- Bot（业务 Bot）：消费 APEX 任务并编排中间件 Service 的业务进程。
- Service（中间件 Service）：
  - Auth Service（auth-service）：用户鉴权与权限校验。
  - Ticket Service（ticket-service）：封装 Jira 操作（查询、创建、更新、删除 Issue 等）。
  - Wiki Service（wiki-service）：封装 Confluence 操作（页面查询、生成、更新等）。
  - Mattermost Service（mattermost-service）：封装通知发送。
- Issue Type：Jira 的 issueType 名称。不得硬编码：
  - Task-Import/Export 默认操作 issueType=Task，但可通过程序配置修改。
  - Case-Import/Export 默认在程序配置中有缺省值，用户可在 Excel 的“设置”Sheet 中覆盖。
- Excel 模板/文件：
  - Import 类任务：APEX 任务附带 Excel 文件作为输入。
  - Export 类任务：APEX 任务提供筛选条件，系统生成 Excel 并回传到 APEX。
- 轮询与回写：
  - 任务轮询间隔：3 秒。
  - 进度回写间隔：3 秒。

三、总体架构与数据流
1. Bot 定时（3 秒）向 APEX API 拉取待处理任务。
2. Bot 调用 Auth Service 校验当前用户是否具备对应操作权限。
3. Bot 编排 Ticket Service、Wiki Service、Mattermost Service 完成具体业务操作：
   - 与 Jira 的读写统一通过 Ticket Service。
   - 与 Confluence 的读写统一通过 Wiki Service。
   - 通知消息统一通过 Mattermost Service。
4. Bot 将处理结果与进度回写到 APEX API；Export 类任务还会将生成的 Excel 文件上传到 APEX。

四、中间件 Service 职责边界
- Auth Service
  - 输入：用户身份、目标操作/资源。
  - 输出：是否有权限及必要的上下文（如项目、权限范围）。
- Ticket Service
  - 输入：业务语义化请求（如按条件查询 Issue、批量创建/更新/删除）。
  - 输出：Jira 数据对象或操作结果。
  - 配置：Issue Type 名称通过配置与/或 Excel 设置覆盖。业务bot端所使用的具体业务操作的field名称，是通过mapping设置的，因为不同的jira环境里，可能会使用类型相同，但是名称不同的field作为对象。
- Wiki Service
  - 输入：页面模板、数据、目标空间/父子层级等。
  - 输出：Confluence 页面创建/更新结果或查询结果。
- Mattermost Service
  - 输入：频道/用户、消息体。
  - 输出：发送结果。

五、业务 Bot 分类与职责
说明：共 10 个 Bot，分 3 类；以下先明确“批量导入/导出类”（5 个）

A. 批量导入/导出类（5 个）
1) Task-Import（task-imp）
   - 操作对象：Jira Issue，issueType 默认为 Task（可在程序配置中修改，不硬编码）。
   - 输入：APEX API 任务 + 用户上传的 Excel 文件。
   - 步骤：
     a. 调用 Auth Service 校验用户权限。
     b. 解析 Excel，得到新增/更新/删除的规则与数据。
     c. 调用 Ticket Service 将 Excel 内容批量写入 Jira（新增/更新/删除）。
   - 输出：处理结果与进度回写到 APEX；必要时通过 Mattermost 通知。

2) Task-Export（task-exp）
   - 操作对象：Jira Issue，issueType 默认为 Task（可配置）。
   - 输入：APEX API 任务（包含筛选条件，不包含 Excel）。
   - 步骤：
     a. 调用 Auth Service 校验用户权限。
     b. 调用 Ticket Service 按任务条件查询 Jira 数据。
     c. 按模板生成 Excel。
     d. 将生成的 Excel 上传回 APEX。
   - 输出：进度与结果回写到 APEX。

3) Case-Import（case-imp）
   - 操作对象：与 Case 相关的 Jira Issue Type（默认值在程序配置中；用户可在 Excel 的“设置”Sheet 中覆盖）。
   - 输入：APEX API 任务 + 用户上传的 Excel 文件。
   - 步骤：
     a. 调用 Auth Service 校验用户权限。
     b. 解析 Excel，得到 Case 相关数据与规则。
     c. 调用 Ticket Service 将数据批量写入 Jira（新增/更新/删除）。
   - 输出：进度与结果回写到 APEX。

4) Case-Export（case-exp）
   - 操作对象：与 Case 相关的 Jira Issue Type（默认值在程序配置中；可由 Excel 设置覆盖）。
   - 输入：APEX API 任务（包含筛选条件，不包含 Excel）。
   - 步骤：
     a. 调用 Auth Service 校验用户权限。
     b. 调用 Ticket Service 按任务条件查询 Jira 中的 Case 相关数据。
     c. 按模板生成 Excel。
     d. 将 Excel 上传回 APEX。
   - 输出：进度与结果回写到 APEX。

5) Indication-Import（indication-imp）
   - 操作对象：与 Indication 相关的 Jira Issue Type（具体名称通过程序配置，避免硬编码；用户可在 confluence 的“设置”table 中覆盖）。
   - 输入：APEX API 任务 + 用户根据雏形做好的confluence页面。
   - 步骤与输出：与 Import 类一致（权限校验 → 解析 confluence页面 → Ticket Service 批量写入 → 回写confluence → 回写进度/结果）。



六、配置与可变项
- Issue Type 名称：不硬编码
  - 全局默认：程序配置文件提供默认 Issue Type（如 Task、Case 相关类型、Indication）。
  - 任务级覆盖：Case（以及需要时的 Indication）可由 Excel 的“设置”Sheet 覆盖具体 Issue Type。
- 模板配置：Export 类 Excel 模板、Confluence 页面模板（由 Wiki Service 使用）在配置中定义。
- 轮询/回写间隔：默认 3 秒，可通过配置调整。

七、进度回写与幂等性（执行约束）
- Bot 在处理过程中每 3 秒将当前进度与状态回写到 APEX API。
- 对外部系统（尤其是 Jira）的写入操作需具备幂等性设计（例如通过外部键或去重逻辑避免重复写入），以适配轮询与重试。
