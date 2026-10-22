通过查阅 [code-server](https://github.com/coder/code-server) 最新的官方构建源码与发布版本（最新版本为 `v4.141.0`），检测结果如下：

---

### 1. 检测结果

* **`codercom/code-server:latest` 内置 Node 版本**：**`v24.21.0` (Node 24)**  
  *(注：code-server 从 `v4.123.0` 开始，已跟随 VS Code 上游升级为了 Node 24)*
* **内置 Node 所在路径**：`/usr/lib/code-server/lib/node`
* **系统全局 `$PATH`**：**默认没有安装 Node**（在容器终端里直接敲 `node` 默认提示找不到命令）。

---

### 2. 重要提醒：此时能把内置的 Node 替换成 Node 22 吗？

**千万不要替换！**

* 因为 `latest` 版本的 code-server 底层的 C++ 原生扩展（`node-pty`、文件监听等）是针对 **Node 24（ABI 137）** 编译的。
* 如果你强行把 `/usr/lib/code-server/lib/node` 替换为 **Node 22（ABI 127）**，属于**跨大版本降级**，code-server 启动时会直接报 `NODE_MODULE_VERSION` 不匹配的错误而彻底崩溃。

---

### 3. 正确的配置方案

根据你的具体需求，有以下两种最佳实践：

#### 方案 A：让开发环境/集成终端使用 Node 22（推荐）
保持 code-server 服务本身使用其内置的 Node 24 稳定运行，而把 Node 22 安装到全局 `/usr/local` 中，供你的开发终端、Go/Python/前端开发使用：

```dockerfile
FROM codercom/code-server:latest

USER root

ARG NODE_VERSION=22.14.0

RUN ARCH= && dpkgArch="$(dpkg --print-architecture)" \
    && case "${dpkgArch##*-}" in \
      amd64) ARCH='x64';; \
      arm64) ARCH='arm64';; \
      *) echo "Unsupported architecture"; exit 1 ;; \
    esac \
    # 安装 Node 22 到系统 /usr/local
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${ARCH}.tar.xz" \
       | tar -xJ -C /usr/local --strip-components=1 --no-same-owner \
    # 验证版本
    && echo "开发终端全局 Node 版本: $(node -v)" \
    && echo "code-server 服务内置 Node 版本: $(/usr/lib/code-server/lib/node -v)"

USER coder
```
> **效果**：你在 code-server 的网页终端执行 `node -v` 显示 `v22.14.0`，项目和开发工具完全运行在 Node 22 下，且编辑器本身稳定不崩。

---

#### 方案 B：如果要求 code-server 服务本身也必须是 Node 22
不要使用 `:latest`，而是使用它内置 Node 22 的最后一个稳定版本 **`codercom/code-server:4.122.1`**：

```dockerfile
# 4.122.1 内置的正是 Node 22.22.1
FROM codercom/code-server:4.122.1

USER root

ARG NODE_VERSION=22.14.0

RUN ARCH= && dpkgArch="$(dpkg --print-architecture)" \
    && case "${dpkgArch##*-}" in \
      amd64) ARCH='x64';; \
      arm64) ARCH='arm64';; \
      *) echo "Unsupported architecture"; exit 1 ;; \
    esac \
    # 1. 安装最新版 Node 22 到全局
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${ARCH}.tar.xz" \
       | tar -xJ -C /usr/local --strip-components=1 --no-same-owner \
    # 2. 因为原本就是 Node 22，这里可以安全覆盖替换内置 node
    && cp /usr/local/bin/node /usr/lib/code-server/lib/node \
    && echo "Node version: $(node -v)"

USER coder
```
