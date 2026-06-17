请你作为资深 Python 代码审查员和业务分析师，**在完全理解代码实现的基础上**，分析当前 Python source code，并整理出系统的业务处理 flow。

重要要求：

1. **不要修改任何代码。**
2. 不要只做表面总结，必须基于实际代码逻辑进行分析。
3. 每一个结论都要尽量标明对应的：

   * 文件名
   * 方法名 / 类名
   * 行号范围
4. 如果某些信息代码中无法确认，请明确写成「代码中未确认」「根据上下文推测」，不要猜测成事实。
5. 请优先从入口点开始分析，例如：

   * CLI entry point
   * main function
   * API route / controller
   * job / batch / scheduler
   * service 层调用
   * 重要的业务方法

---

## 你的分析步骤

请按照下面步骤进行。

### Step 1：整体代码结构理解

先扫描项目结构，说明：

* 主要目录结构
* 每个重要文件 / 模块的职责
* 入口文件在哪里
* 核心业务类 / 方法有哪些
* 主要外部依赖有哪些，例如：

  * DB
  * API
  * file I/O
  * message queue
  * environment variables
  * config files
  * command line arguments

输出格式：

| 文件 / 目录 | 职责 | 重要类 / 方法 | 备注 |
| ------- | -- | -------- | -- |

---

### Step 2：业务 flow 总览

请先用整体视角整理主要业务 flow。

每个 flow 请包含：

* Flow 名称
* 触发入口
* 入口文件和行号
* 主要处理步骤
* 涉及的核心方法调用顺序
* 最终输出 / 副作用

输出格式：

## Flow 1：xxx

入口：

* 文件：`xxx.py`
* 方法：`xxx()`
* 行号：Lxx-Lxx

整体调用链：

```text
xxx.py:L10 main()
  -> service.py:L35 process_xxx()
    -> validator.py:L20 validate_xxx()
    -> repository.py:L50 save_xxx()
```

业务目的：

* xxx

最终输出：

* return 值：
* 写入文件：
* 写入 DB：
* 调用外部 API：
* log：
* error：

---

### Step 3：按照业务 flow 详细展开

请按照每一个业务 flow，详细说明每一步。

每一步必须包含：

1. 当前步骤做什么
2. 所属文件、方法、行号
3. input 是什么
4. output 是什么
5. 关键变量有哪些
6. 关键变量可能的值有哪些
7. 事前 check / validation 有哪些
8. 分歧条件有哪些
9. 可能发生的 error / exception / error message 有哪些
10. 失败时 flow 如何结束或继续

输出格式：

## Flow 1：xxx 详细分析

### Step 1.1：xxx

位置：

* 文件：`xxx.py`
* 方法：`xxx()`
* 行号：Lxx-Lxx

Input：

| 变量名 | 类型 | 来源 | 可能的值 | 说明 |
| --- | -- | -- | ---- | -- |

处理逻辑：

1. xxx
2. xxx
3. xxx

事前 check / validation：

| Check 内容 | 条件 | 失败时行为 | Error message | 代码位置 |
| -------- | -- | ----- | ------------- | ---- |

分歧逻辑：

| 条件 | True 时 | False 时 | 代码位置 |
| -- | ------ | ------- | ---- |

Output：

| 输出对象 | 类型 | 输出到哪里 | 说明 |
| ---- | -- | ----- | -- |

可能的 error：

| Error / Exception | 触发条件 | Error message | 是否被 catch | 代码位置 |
| ----------------- | ---- | ------------- | --------- | ---- |

---

### Step 1.2：xxx

同样格式继续分析。

---

### Flow 分歧说明

如果一个方法内部存在 if / elif / else / try / except / return early，请整理成下面格式：

```text
method_name()
├─ check A failed
│  └─ return / raise xxx
├─ check B failed
│  └─ return / raise xxx
├─ condition C == true
│  └─ call xxx()
└─ condition C == false
   └─ call yyy()
```

每个分支必须注明：

* 条件表达式
* 条件中使用的变量
* 变量可能的值
* 分支对应的业务含义
* 文件名和行号
* 可能的 error message

---

## Step 4：方法级别详细说明

请列出每个核心方法的详细说明。

输出格式：

## 方法：`xxx()`

位置：

* 文件：`xxx.py`
* 行号：Lxx-Lxx
* 所属类：`XxxClass`，如果没有则写 None

方法职责：

* xxx

参数：

| 参数名 | 类型 | 默认值 | 来源 | 可能的值 | 说明 |
| --- | -- | --- | -- | ---- | -- |

返回值：

| 类型 | 可能的值 | 说明 |
| -- | ---- | -- |

内部处理步骤：

1. xxx
2. xxx
3. xxx

事前 check：

| Check | 条件 | 失败时行为 | Error message | 行号 |
| ----- | -- | ----- | ------------- | -- |

分歧：

| 条件 | 业务含义 | True 时 | False 时 | 行号 |
| -- | ---- | ------ | ------- | -- |

调用的其他方法：

| 被调用方法 | 文件 | 行号 | 调用目的 |
| ----- | -- | -- | ---- |

可能的异常 / error message：

| Error / Exception | message | 触发条件 | 是否被捕获 | 行号 |
| ----------------- | ------- | ---- | ----- | -- |

---

## Step 5：变量和值域分析

请整理核心变量、配置项、状态值、flag、enum-like 字符串。

输出格式：

| 变量名 | 定义位置 | 使用位置 | 类型 | 可能的值 | 值的来源 | 业务含义 |
| --- | ---- | ---- | -- | ---- | ---- | ---- |

特别注意：

* config 读取值
* environment variables
* command line arguments
* request parameter
* DB field
* hard-coded constant
* status / type / mode / flag
* True / False 分支
* None / empty string / empty list 的特殊处理

---

## Step 6：error message / exception 总整理

请把所有可能出现的 error、exception、log error、return error 统一整理。

输出格式：

| Error message / Exception | 触发条件 | 所属 flow | 文件 | 方法 | 行号 | 后续处理 |
| ------------------------- | ---- | ------- | -- | -- | -- | ---- |

请包括：

* `raise`
* `assert`
* `try / except`
* `logger.error`
* `logger.warning`
* error response
* return error code
* validation failed
* file not found
* config missing
* API failed
* DB failed

---

## Step 7：最终业务说明文档

最后，请输出一份面向业务人员和开发人员都能理解的说明文档。

文档结构如下：

# 业务 Flow 分析报告

## 1. 系统概要

## 2. 主要业务 Flow 一览

## 3. Flow 1：xxx

### 3.1 触发条件

### 3.2 Input

### 3.3 处理步骤

### 3.4 分歧逻辑

### 3.5 Output

### 3.6 Error / Exception

### 3.7 涉及文件和方法

## 4. Flow 2：xxx

同样格式继续。

## 5. 核心变量和值域

## 6. 事前 Check 总整理

## 7. Error Message 总整理

## 8. 代码中无法确认但需要业务确认的点

请列出：

| 不明点 | 相关代码位置 | 为什么无法确认 | 建议向谁确认 |
| --- | ------ | ------- | ------ |

---

## 额外要求

* 请尽量使用 Markdown 表格。
* 代码位置必须尽量精确到文件名和行号。
* 不要省略重要分支。
* 不要只解释函数名，要解释实际业务含义。
* 如果 flow 很长，请先输出整体 flow，再逐个 flow 深挖。
* 如果代码量太大，请先找出最核心的入口和主 flow，再说明哪些部分还需要继续分析。
