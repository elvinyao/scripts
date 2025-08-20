请告诉我如何使用 Claude Code 或 Gemini CLI 针对该项目进行日志和错误处理的改进：

1. 实现新的 Logger 初始化方式，支持通过外部参数设置日志级别（log level）和日志格式（log format）。
2. 日志格式需支持三种类型：business、internal_access 和 external_access，并在日志中明确标识。
   - internal_access 用于记录 FastAPI 中 uvicorn 的访问日志，且按指定格式输出。
   - external_access 额外记录 FastAPI 对外部系统（如 Jira、Confluence）的每次请求。
3. 日志系统需支持 traceid，在业务服务中新建用户任务时生成 traceid，并传递给相关调用链。
4. 增加专门的 Logger，用于类似 Tomcat 记录外部访问自身的方式，详细记录每次对 Jira、Confluence 等 REST API 的请求。

错误处理方面：
- 实现分层错误类，包括 SystemError 和 BusinessError，定义必要属性。
- 根据业务调用关系，对现有代码进行事前检查，包括业务逻辑校验、对外部系统调用、内部中间服务调用，以及单独针对 Jira 调用的检查。
