很棒的重构计划！你提到还需要统一接入 **common 里的 logger、自定义异常类、HTTP 客户端**。下面给出一套**放在哪里、如何串起来、如何落地到测试/API/CLI**的做法与最小可行代码示例，直接可套进你现有的步骤中。

---

# 放在哪里（目录建议）

假设你的项目名为 `my_application`，推荐把「可复用、与业务无关」的东西集中到 `common/`，并把它当成一个**稳定依赖层**（越靠下越基础）：

```
my_application/
├─ pyproject.toml / setup.cfg / requirements.txt
├─ src/
│  └─ my_application/
│     ├─ common/                # 可复用基础设施层（logger、异常、HTTP 客户端）
│     │  ├─ __init__.py
│     │  ├─ logging.py          # 统一日志配置 & 工厂
│     │  ├─ exceptions.py       # 基础异常层级 & 错误码
│     │  └─ http/
│     │     ├─ __init__.py
│     │     ├─ client.py        # HttpClient 协议/实现/中间件（重试、超时、指标）
│     │     └─ types.py         # （可选）请求/响应类型定义
│     ├─ core/                  # 纯领域逻辑，不依赖具体实现（可依赖 common 的接口）
│     ├─ services/              # 应用服务（编排 core 与外部系统）
│     ├─ adapters/
│     │  ├─ http/               # 具体三方服务适配器（调用 common.http）
│     │  └─ repo/
│     ├─ api/
│     │  ├─ fastapi_app.py      # API 入口（日志中间件、异常映射）
│     │  └─ handlers.py
│     └─ cli/
│        └─ main.py             # CLI 入口（初始化日志、加载配置）
└─ tests/
   ├─ common/
   ├─ core/
   ├─ services/
   └─ adapters/
```

> 如果你有多服务/单体多模块，`common/` 甚至可以抽到 `libs/common/` 作为**独立包**在 monorepo 里被多个应用复用（`pip install -e libs/common`）。

---

# 怎么进行（落地步骤）

下面的步骤可直接插入你原来的第 3～6 步中执行。

## 1) 统一日志（common/logging.py）

* **只在应用入口**（如 `api/fastapi_app.py`、`cli/main.py`）调用一次 `setup_logging()`。
* 业务代码里**只 get，不配置**：`logger = get_logger(__name__)`。
* 建议 JSON 结构化日志 + 上下文（如 trace\_id / request\_id）：

```python
# src/my_application/common/logging.py
from __future__ import annotations
import logging
import logging.config
import os
import contextvars
from typing import Dict, Any

_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

def set_request_id(rid: str | None) -> None:
    _request_id.set(rid)

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id.get() or "-"
        return True

def setup_logging(level: str | None = None) -> None:
    level = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": { "request_id": {"()": RequestIdFilter} },
        "formatters": {
            "json": {
                "format": '{"ts":"%(asctime)s","lvl":"%(levelname)s","logger":"%(name)s",'
                          '"msg":"%(message)s","request_id":"%(request_id)s"}'
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "filters": ["request_id"],
                "formatter": "json",
            }
        },
        "root": { "handlers": ["stdout"], "level": level },
    }
    logging.config.dictConfig(config)

def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)
```

**接入点：**

* FastAPI：在中间件里生成/传播 `request_id`，并在请求生命周期内 `set_request_id()`。
* CLI：启动时生成一个随机运行 ID（或从环境注入）。

## 2) 自定义异常体系（common/exceptions.py）

* 目标：**域层/服务层抛清晰可枚举的业务异常**，适配器/边界层负责「**异常到协议**」的映射（比如 HTTP 404/409/503）。
* 保持**可机器处理的 error\_code**，方便日志、指标与前端。

```python
# src/my_application/common/exceptions.py
from __future__ import annotations
from typing import Any, Optional

class AppError(Exception):
    code: str = "internal_error"
    http_status: int = 500
    retryable: bool = False

    def __init__(self, message: str = "", *, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}

# 领域/通用错误
class ValidationError(AppError):
    code = "validation_error"
    http_status = 400

class NotFoundError(AppError):
    code = "not_found"
    http_status = 404

class ConflictError(AppError):
    code = "conflict"
    http_status = 409

class ExternalServiceError(AppError):
    code = "external_service_error"
    http_status = 502
    retryable = True

class TimeoutError(AppError):
    code = "timeout"
    http_status = 504
    retryable = True
```

**API 映射（FastAPI 举例）：**

```python
# src/my_application/api/fastapi_app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from my_application.common.logging import setup_logging, set_request_id, get_logger
from my_application.common.exceptions import AppError
import uuid

app = FastAPI()
setup_logging()
log = get_logger(__name__)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    set_request_id(rid)
    response = await call_next(request)
    response.headers["x-request-id"] = rid
    return response

@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError):
    return JSONResponse(status_code=exc.http_status, content=exc.to_dict())
```

> 这样，领域/服务层只需 `raise NotFoundError("user not found", details={"user_id": 1})`，API 层就能自动得到 404 + 稳定结构的响应。

## 3) 统一 HTTP 客户端（common/http/client.py）

* 目标：**对外只暴露一个协议/接口**，内部可换实现（如 `httpx`/`requests`/mock）。
* 固化默认：**合理超时、重试（幂等请求）、错误转译（到 AppError）**、埋点与日志。

```python
# src/my_application/common/http/client.py
from __future__ import annotations
from typing import Protocol, Any, Mapping, Optional
import httpx
from my_application.common.exceptions import ExternalServiceError, TimeoutError
from my_application.common.logging import get_logger

log = get_logger(__name__)

class HttpClient(Protocol):
    async def get(self, url: str, *, params: Optional[Mapping[str, Any]] = None, headers: Optional[Mapping[str, str]] = None, timeout: Optional[float] = None) -> httpx.Response: ...
    async def post(self, url: str, *, json: Any = None, headers: Optional[Mapping[str, str]] = None, timeout: Optional[float] = None) -> httpx.Response: ...
    # 按需补充 put/patch/delete...

class HttpxClient(HttpClient):
    def __init__(self, *, base_url: str = "", default_timeout: float = 5.0, max_retries: int = 2):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=default_timeout)
        self._max_retries = max_retries

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = await self._client.request(method, url, **kwargs)
                if 500 <= resp.status_code < 600:
                    # 5xx 视为外部错误（可重试）
                    raise ExternalServiceError(f"Upstream {method} {url} returned {resp.status_code}",
                                               details={"status": resp.status_code, "body": _safe_body(resp)})
                return resp
            except httpx.TimeoutException as e:
                last_exc = e
                if attempt == self._max_retries:
                    raise TimeoutError(f"Upstream timeout: {method} {url}") from e
                log.warning("http_timeout_retry", extra={"method": method, "url": url, "attempt": attempt + 1})
            except ExternalServiceError as e:
                last_exc = e
                if attempt == self._max_retries:
                    raise
                log.warning("http_5xx_retry", extra={"method": method, "url": url, "attempt": attempt + 1})
            except httpx.HTTPError as e:
                # 连接错误等，按需判定是否可重试
                last_exc = e
                if attempt == self._max_retries:
                    raise ExternalServiceError(f"HTTP error: {method} {url}", details={"error": str(e)}) from e
                log.warning("http_error_retry", extra={"method": method, "url": url, "attempt": attempt + 1})
        assert last_exc is not None
        raise last_exc

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, **kwargs)

    async def aclose(self) -> None:
        await self._client.aclose()

def _safe_body(resp: httpx.Response) -> str:
    try:
        return resp.text[:512]
    except Exception:
        return "<unreadable>"
```

**适配器使用（调用第三方服务）**：

```python
# src/my_application/adapters/http/user_service.py
from __future__ import annotations
from typing import Any
from my_application.common.http.client import HttpClient
from my_application.common.exceptions import NotFoundError

class UserService:
    def __init__(self, client: HttpClient):
        self._c = client

    async def get_user(self, user_id: str) -> dict[str, Any]:
        resp = await self._c.get(f"/users/{user_id}")
        if resp.status_code == 404:
            raise NotFoundError("user not found", details={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()
```

**在应用入口注入**（FastAPI 为例）：

```python
# src/my_application/api/fastapi_app.py (节选)
from fastapi import Depends
from my_application.common.http.client import HttpxClient
from my_application.adapters.http.user_service import UserService

# 简单的“容器”
http_client = HttpxClient(base_url="https://example.com", default_timeout=5.0, max_retries=2)
user_service = UserService(http_client)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return await user_service.get_user(user_id)
```

> 更正式的 DI 可以用 `dependency-injector / punq` 等；小型项目用上面这种“模块级单例 + Depends”也够用。

---

# 与你的重构步骤如何对齐

* **第 3 步（模块化）**：把 logger、异常、HTTP 客户端放进 `common/`；业务模块（`core/`、`services/`、`adapters/`）**只依赖接口/基类**。
* **第 4 步（测试）**：

  * 为 `exceptions.py` 写最简单的构造/序列化测试。
  * 为 `HttpxClient` 写超时/5xx 重试的单测（mock `httpx.AsyncClient.request`）。
  * 业务/适配器测试时，用 **FakeHttpClient**（实现同名协议，不发真实请求）：

    ```python
    class FakeHttpClient:
        def __init__(self, mapping): self.mapping = mapping
        async def get(self, url, **_): return self.mapping[url]
        async def post(self, url, **_): ...
    ```
* **第 5 步（代码质量）**：

  * 在 `setup.cfg/pyproject.toml` 配置 `flake8`、`black`、`isort`、`mypy`，确保 `common/` 作为“标准库”被全项目一致使用。
* **第 6 步（部署）**：

  * 入口点（API/CLI）**唯一**调用 `setup_logging()`。
  * 配置项（base\_url、超时、重试次数、日志级别）从环境变量或配置模块读取（比如 `pydantic-settings`）。

---

# 渐进式迁移清单

1. **替换 print → logger**：在核心路径先替换，保留原行为（级别用 `INFO/DEBUG`，错误用 `exception()` 带堆栈）。
2. **统一异常**：把散落的 `ValueError/KeyError/RuntimeError` 替换为 `ValidationError/NotFoundError/...`，仅在边界层（API/CLI）做一次性映射。
3. **抽换 HTTP**：把直接用 `requests/httpx` 的调用迁移到 `UserService` 这类适配器，底层只走 `common.http.HttpClient`。
4. **增加请求上下文**：为 Web/任务/CLI 建立 request\_id（或 job\_id）并注入日志。
5. **补测试**：从适配器和服务层开始，外部依赖一律 mock/Fake。

---

# 常见坑 & 建议

* **不要在库代码里初始化日志处理器**（避免重复 handler）。只在应用入口 `setup_logging()`。
* **异常不要夹杂 HTTP 语义**到领域层（比如“返回 404”），而是抛 `NotFoundError`，让 API 层决定返回码。
* **HTTP 重试只针对幂等请求**（GET/HEAD/部分 PUT/DELETE），并限制最大重试次数与退避策略。
* **日志不要打印大响应体**（截断、脱敏）。
* **为异常定义稳定 `code`**，避免上层靠字符串匹配 message。

---

如果你把上面的三个组件按此方式落到 `common/`，且在入口处一次性初始化、在业务中只依赖接口，你的项目会非常容易测试与维护。
需要的话，我可以基于你现有的仓库结构，再给一版**精准迁移 diff 计划**（包含 TODO 列表和优先级）。
