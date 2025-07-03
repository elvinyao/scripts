可以，一条管道就能把 \**grep 到的所有 *.yaml 文件** 打进一个 tar.gz 归档，同时保留它们在 `/data` 下的原始目录层级。下面给出一个安全可回滚的做法：

```bash
# 变量定义（旧 token 和输出归档名）
OLD_TOKEN='asdasdasd23232323'
ARCHIVE=/tmp/token_yaml_$(date +%F).tar.gz   # 例：/tmp/token_yaml_2025-07-03.tar.gz

# ① 搜索含旧 token 的 YAML 文件 → 打包进 tar.gz
sudo grep -Rl --include="*.yaml" -F "$OLD_TOKEN" /data \
| sudo tar --create --gzip --absolute-names --files-from=- --file="$ARCHIVE"
```

### 关键点说明

| 选项/步骤                          | 作用                                                                           |                 |
| ------------------------------ | ---------------------------------------------------------------------------- | --------------- |
| `grep -Rl`                     | **-R** 递归、**-l** 仅列文件路径；`-F` 关闭正则解析更安全                                       |                 |
| `--include="*.yaml"`           | 只看 YAML                                                                      |                 |
| 管道 \`                          | \`                                                                           | 直接把文件列表传给 `tar` |
| `tar --create --gzip` (`-czf`) | 创建 gzip 归档                                                                   |                 |
| `--files-from=-`               | 从标准输入读取要打包的路径（横杠 `-` 表示 stdin）                                               |                 |
| `--absolute-names`             | 保留完整绝对路径（如 `/data/dir1/file.yaml`），方便还原；如需去掉开头 `/` 可改用 `--transform='s,^/,,` |                 |
| `--file="$ARCHIVE"`            | 指定输出文件                                                                       |                 |

> **为什么不用 `xargs tar -rf`？**
> `--files-from=-` 一步就能完成；省去 xargs 处理长参数列表时的复杂性，还避免因文件名含空格、换行导致的错包。

---

## 如何确认归档成功

1. **查看归档列表**

   ```bash
   tar -tzf "$ARCHIVE" | head
   ```

   若能看到 `/data/.../*.yaml` 路径，即说明文件已收入归档。
   用 `wc -l` 对比 grep 行数也行：

   ```bash
   FILE_COUNT=$(sudo grep -Rl --include="*.yaml" -F "$OLD_TOKEN" /data | wc -l)
   TAR_COUNT=$(tar -tzf "$ARCHIVE" | wc -l)
   echo "grep: $FILE_COUNT  |  tar: $TAR_COUNT"
   ```

2. **校验完整性**

   ```bash
   gzip -t "$ARCHIVE" && echo "✅ 归档无损坏"
   ```

3. **按需抽取单个文件**

   ```bash
   tar -xzf "$ARCHIVE" -C /tmp/recover/path /data/some/file.yaml
   ```

---

### 进阶：先写入临时清单再打包（可审阅）

```bash
sudo grep -Rl --include="*.yaml" -F "$OLD_TOKEN" /data > /tmp/token_filelist.txt
sudo tar -czf "$ARCHIVE" --absolute-names --files-from=/tmp/token_filelist.txt
```

这样你可以先 **cat /tmp/token\_filelist.txt** 审核路径，确保没有误打包，再执行 tar。

---

完成后就得到了只包含含旧 token 的 YAML 文件的 `tar.gz`，既方便备份，也方便后期 diff 或迁移。
