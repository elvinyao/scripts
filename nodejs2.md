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
