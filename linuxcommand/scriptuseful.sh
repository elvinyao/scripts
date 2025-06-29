以下是常用的 Git、Docker 和 Linux 服务（systemd/service）命令速查表，按「查看状态 / 启动重启 / 查看日志」等类别整理。

1. Git 常用命令
--------------------------------------------------
1.1 仓库操作
  • 克隆仓库：
    git clone <repo_url> [目标目录]
  • 初始化本地仓库：
    git init [目录]

1.2 提交 & 同步
  • 查看状态：
    git status
  • 暂存改动：
    git add <文件或目录>
    git add .    # 全部
  • 提交：
    git commit -m "提交信息"
  • 拉取远程改动并合并：
    git pull [远程名] [分支]
  • 推送本地提交：
    git push [远程名] [分支]

1.3 分支管理
  • 列出分支：
    git branch        # 本地
    git branch -r     # 远程
  • 新建并切换：
    git checkout -b <分支名>
  • 切换分支：
    git checkout <分支名>
  • 合并分支：
    git merge <分支名>
  • 删除分支：
    git branch -d <分支名>

1.4 查看日志 & 差异
  • 历史提交：
    git log
    git log --oneline --graph --all
  • 查看文件改动：
    git diff            # 工作区 vs 暂存区
    git diff HEAD~1     # vs 上一个提交
  • 某次提交内容：
    git show <commit_id>

1.5 其他
  • 暂存/恢复工作区改动：
    git stash
    git stash list
    git stash pop
  • 标签管理：
    git tag               # 列出标签
    git tag v1.0           # 创建标签
    git push --tags        # 推送所有标签
  • 远程仓库：
    git remote -v          # 查看 URL
    git remote add origin <url>

2. Docker 常用命令
--------------------------------------------------
2.1 镜像（images）
  • 拉取镜像：
    docker pull <镜像名>[:标签]
  • 本地镜像列表：
    docker images
  • 构建镜像：
    docker build -t <镜像名>:<标签> .
  • 删除镜像：
    docker rmi <镜像ID或名>

2.2 容器（containers）
  • 查看运行中容器：
    docker ps
  • 查看所有容器：
    docker ps -a
  • 启动容器：
    docker start <容器ID或名>
  • 停止容器：
    docker stop <容器ID或名>
  • 重启容器：
    docker restart <容器ID或名>
  • 删除容器：
    docker rm <容器ID或名>

2.3 运行 & 交互
  • 以交互模式启动：
    docker run -it --name <名> <镜像> /bin/bash
  • 后台运行：
    docker run -d --name <名> <镜像>
  • 查看日志：
    docker logs <容器ID或名>
    docker logs -f <容器ID或名>    # 实时跟踪
  • 进入运行中容器：
    docker exec -it <容器ID或名> /bin/bash

2.4 网络 & 存储
  • 网络列表：
    docker network ls
  • 创建网络：
    docker network create <网名>
  • 数据卷列表：
    docker volume ls
  • 创建卷：
    docker volume create <卷名>

2.5 Docker Compose（v2+）
  • 启动服务：
    docker compose up -d
  • 停止并移除容器：
    docker compose down
  • 查看服务状态：
    docker compose ps
  • 查看日志：
    docker compose logs [-f] [服务名]

3. Linux 服务管理（systemd & service）
--------------------------------------------------
3.1 systemd (推荐)
  • 查看服务状态：
    systemctl status <服务名>.service
  • 启动服务：
    systemctl start <服务名>.service
  • 停止服务：
    systemctl stop <服务名>.service
  • 重启服务：
    systemctl restart <服务名>.service
  • 平滑重载配置：
    systemctl reload <服务名>.service
  • 开机自启：
    systemctl enable <服务名>.service
  • 取消自启：
    systemctl disable <服务名>.service

3.2 兼容命令（老版 init.d）
  • 启停重启：
    service <服务名> start|stop|restart|status

3.3 查看日志
  • journalctl（systemd 日志）：
    journalctl -u <服务名>.service       # 查看该服务日志
    journalctl -u <服务名>.service -f    # 实时跟踪
    journalctl -xe                        # 系统级错误日志
  • 传统日志文件：
    tail -n 100 /var/log/<应用>.log
    tail -f /var/log/syslog 或 /var/log/messages

3.4 常见辅助命令
  • 查看进程：
    ps aux | grep <关键字>
    top / htop
  • 杀掉进程：
    kill <PID>
    pkill <进程名>
  • 端口 & 连接：
    ss -tnlp
    netstat -tnlp
  • 磁盘 & 内存：
    df -h
    du -sh <目录>
    free -m
  • 打开文件列表：
    lsof -i :<端口>

以上命令覆盖了日常绝大多数场景，按需组合使用即可快速定位、管理和排查问题。
