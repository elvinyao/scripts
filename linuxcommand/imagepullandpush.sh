#!/usr/bin/env bash
set -euo pipefail

#
# 配置区 —— 请根据实际情况修改下面变量
#
# 源 Nexus A（公开，不需要登录 pull）
SRC_HOST="nexus-a.company.com"
SRC_PORT="8082"
SRC_REPO="docker-hosted"
IMAGE_NAME="myapp"
IMAGE_TAG="1.0"

# 目标 Nexus B（需要登录 push）
DEST_HOST="nexus-b.company.com"
DEST_PORT="8082"
DEST_REPO="docker-hosted"
DEST_USER="bob"
DEST_PASS="b0bPass"
# /配置区

SRC_IMAGE="${SRC_HOST}:${SRC_PORT}/${SRC_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
DEST_IMAGE="${DEST_HOST}:${DEST_PORT}/${DEST_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"

echo ">>> Pulling image from Nexus A:"
echo "    docker pull ${SRC_IMAGE}"
docker pull "${SRC_IMAGE}"

echo ">>> Retag image for Nexus B:"
echo "    docker tag ${SRC_IMAGE} ${DEST_IMAGE}"
docker tag "${SRC_IMAGE}" "${DEST_IMAGE}"

echo ">>> Login to Nexus B (${DEST_HOST}:${DEST_PORT})"
# 推荐使用 --password-stdin，避免明文出现在 ps 列表
echo "${DEST_PASS}" | docker login "${DEST_HOST}:${DEST_PORT}" \
                       -u "${DEST_USER}" \
                       --password-stdin

echo ">>> Push image to Nexus B:"
echo "    docker push ${DEST_IMAGE}"
docker push "${DEST_IMAGE}"

echo ">>> Logout from Nexus B"
docker logout "${DEST_HOST}:${DEST_PORT}"

echo ">>> Done!"
