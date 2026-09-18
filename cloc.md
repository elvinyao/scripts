可以。**日期范围交给 Git 筛选，`cloc` 负责比较两个 commit，并限定要统计的目录。** 不过要区分：你要的是“这段时间前后的代码差异”，还是“这段时间每次提交的累计改动量”。这两种结果不一样。([GitHub][1])

## 1. 指定日期范围＋文件夹，统计代码差异

例如，统计 **2026 年 9 月 1 日～9 月 15 日，`src/` 和 `backend/` 目录的变化**。

在 Git 仓库根目录执行。下面使用 Bash/Zsh 语法，Windows 可在 Git Bash 中执行：

```bash
# 要统计的分支：HEAD 表示当前版本，也可以改成 main、develop 等
REF=HEAD

# 起点：统计开始日期之前的最后一个版本
BASE=$(git rev-list --first-parent -1 \
  --until="2026-08-31 23:59:59 +0900" "$REF")

# 终点：统计结束日期当天结束时的最后一个版本
END=$(git rev-list --first-parent -1 \
  --until="2026-09-15 23:59:59 +0900" "$REF")

# 检查版本是否存在，再进行统计
if [ -z "$BASE" ] || [ -z "$END" ]; then
  echo "未找到起止版本，请检查日期、分支，以及 Git 历史是否完整。" >&2
else
  cloc --git-diff-rel "$BASE" "$END" \
    --match-d='(^|/)(src|backend)(/|$)' \
    --by-file
fi
```

这里使用 `--first-parent` 沿目标分支的第一父提交历史选取版本，避免选到合并进来的旁支上的某个版本；`+0900` 表示日本时间。**起点应当取开始日期之前的版本，而不是期间内的第一条提交，否则会漏掉第一条提交本身的改动。**([Git][2])

`cloc` 参数含义如下。([GitHub][1])

| 参数                              | 作用                 |            |      |                                 |
| ------------------------------- | ------------------ | ---------- | ---- | ------------------------------- |
| `--git-diff-rel "$BASE" "$END"` | 比较两个 Git 版本中有变化的文件 |            |      |                                 |
| `--match-d='(^                  | /)(src             | backend)(/ | $)'` | 只统计路径中含 `src` 或 `backend` 目录的文件 |
| `--by-file`                     | 按文件展示；去掉则默认按语言汇总   |            |      |                                 |

**注意：这是两个版本的最终差异，不是中间所有提交的累计工作量。** 例如，期间新增一个文件，后来又删除，最终两个版本都没有它，那么这次比较不会体现中间的新增、删除过程。

## 2. 文件夹限制怎么改？

修改 `--match-d` 即可。它使用正则表达式匹配目录路径；排除目录可以使用 `--exclude-dir`。([GitHub][1])

```bash
# 只统计 src 目录及其子目录
--match-d='(^|/)src(/|$)'

# 统计 src、backend 两类目录
--match-d='(^|/)(src|backend)(/|$)'

# 只统计路径中 backend/src 这一段下面的文件
--match-d='(^|/)backend/src(/|$)'

# 排除这些名称的目录
--exclude-dir=node_modules,vendor,dist,build
```

这些正则匹配的是**路径片段**，所以也会匹配更深层的同名目录，例如 `packages/demo/src/`，不只限于仓库根目录下的 `src/`。

需要导出逐文件 CSV 报表，可以在上面成功取得 `BASE` 和 `END` 后执行：([GitHub][1])

```bash
cloc --git-diff-rel "$BASE" "$END" \
  --match-d='(^|/)(src|backend)(/|$)' \
  --exclude-dir=node_modules,vendor,dist,build \
  --by-file --csv --out=cloc-report.csv
```

## 3. 如果要统计“期间所有提交累计改了多少行”

这时直接用 **`git log --numstat`** 更合适。下面按日期筛选当前版本历史中的非合并提交，再累计指定目录的新增、删除行数。([Git][3])

```bash
git log HEAD \
  --since-as-filter="2026-09-01 00:00:00 +0900" \
  --until="2026-09-15 23:59:59 +0900" \
  --no-merges \
  --numstat --format= \
  -- src/ backend/ |
awk '
  $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ {
    added += $1
    deleted += $2
  }
  END {
    printf "累计新增：%d 行\n累计删除：%d 行\n新增减删除：%d 行\n",
           added, deleted, added - deleted
  }
'
```

这里统计的是**文本行**，包含注释和空行，不是 `cloc` 意义上的纯代码行；二进制文件被上面的 `awk` 跳过。`--no-merges` 排除了合并提交，因此合并时独有的冲突修正也不会计入。([Git][3])

**看某段时间“项目最终变了多少”，用第 1 种；看“各次提交累计增删多少行”，用第 3 种。**

[1]: https://github.com/AlDanial/cloc "GitHub - AlDanial/cloc: cloc counts blank lines, comment lines, and physical lines of source code in many programming languages. · GitHub"
[2]: https://git-scm.com/docs/git-rev-list "Git - git-rev-list Documentation"
[3]: https://git-scm.com/docs/git-log "Git - git-log Documentation"
