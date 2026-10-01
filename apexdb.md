我看到的某个旧版的 tablespace_name 查询到的max 大小，应该是 在instance里创建workspace里， 选择的Space Quota（MB），选择的2000. 现在这个正在使用，我可以怎么调整这个值吗

对，你这个判断基本正确。

如果你查的是 `DBA_TS_QUOTAS.MAX_BYTES`，而它正好显示约 **2000 MB**，那么它大概率就是当初创建 APEX Workspace 时 `Space Quota (MB) = 2000` 最终设置到对应数据库 Schema 上的 tablespace quota。Oracle 文档也说明这个 `Space Quota` 后续可以调整。[Oracle Docs](https://docs.oracle.com/database/apex-5.1/AEADM/creating-workspaces.htm?utm_source=chatgpt.com)

### 最直接的调整方法：ALTER USER

先确认：

```sql
SELECT
    username,
    tablespace_name,
    ROUND(bytes / 1024 / 1024) AS used_mb,
    CASE
        WHEN max_bytes = -1 THEN -1
        ELSE ROUND(max_bytes / 1024 / 1024)
    END AS quota_mb
FROM dba_ts_quotas
WHERE username = '你的_SCHEMA_NAME';
```

比如现在：

```text
USERNAME     TABLESPACE_NAME   USED_MB   QUOTA_MB
----------- ----------------- --------- --------
MYAPP        MYAPP             1650      2000
```

那么可以直接改成 5GB：

```sql
ALTER USER MYAPP
QUOTA 5000M ON MYAPP;
```

或者：

```sql
ALTER USER MYAPP
QUOTA 5G ON MYAPP;
```

**这是在线修改。APEX 正在运行也可以改，不需要停 APEX、ORDS 或数据库，也不需要重启。**

Oracle 明确支持在用户创建之后增加或修改 tablespace quota。[Oracle Docs](https://docs.oracle.com/database/121/DBSEG/users.htm?utm_source=chatgpt.com)

改完确认：

```sql
SELECT
    username,
    tablespace_name,
    ROUND(bytes / 1024 / 1024) used_mb,
    ROUND(max_bytes / 1024 / 1024) quota_mb
FROM dba_ts_quotas
WHERE username = 'MYAPP';
```

应该就会变成：

```text
MYAPP   MYAPP   1650   5000
```

### APEX Admin 里面也可以走正式流程

旧版 APEX 还有一套“增加 Workspace Storage”的机制。

Workspace Administrator：

```text
Administration
  → Manage Service
    → Make a Service Request
      → Request Storage
```

选择例如增加：

```text
+1000 MB
+2000 MB
...
```

然后 Instance Administrator：

```text
APEX Administration Services
  → Manage Requests
    → All Change Requests
      → View Request
        → Add Space
```

批准即可。Oracle APEX 5.1 官方文档就是这样描述的。[Oracle Docs](https://docs.oracle.com/database/apex-5.1/AEADM/making-a-service-request.htm?utm_source=chatgpt.com)

所以如果你是 **DBA，直接 `ALTER USER ... QUOTA` 最简单**；如果要遵循旧 APEX 自己的管理流程，则走 `Request Storage → Add Space`。

---

但这里还有一个非常重要的区别：

```text
Workspace / Schema quota
        ↓
2000 MB → 5000 MB
```

**不代表真正的 tablespace 有 5GB 可用。**

例如：

```text
Schema quota             5000 MB
          ↓
Tablespace datafile
          ↓
当前物理大小              3000 MB
最大可扩展               10000 MB
```

这是没问题的，因为 datafile 可以继续 autoextend。

反过来如果：

```text
Schema quota             5000 MB
Tablespace MAXSIZE       3000 MB
```

那你即使把 quota 改成 5000MB，实际也用不到 5000MB。

所以建议你再跑一下：

```sql
SELECT
    tablespace_name,
    file_name,
    ROUND(bytes / 1024 / 1024) AS current_mb,
    autoextensible,
    ROUND(maxbytes / 1024 / 1024) AS max_mb
FROM dba_data_files
WHERE tablespace_name = '你的_TABLESPACE_NAME';
```

你现在如果看到的是类似：

```text
DBA_TS_QUOTAS
TABLESPACE_NAME   BYTES        MAX_BYTES
XXX               1.6GB        2GB
```

那么**100%应该改的是 Schema Quota，而不是 resize datafile**。

最简单就是：

```sql
ALTER USER <APEX_SCHEMA>
QUOTA 5G ON <TABLESPACE>;
```

这也是我更推荐你现在采用的方法。[Oracle Docs](https://docs.oracle.com/database/121/DBSEG/users.htm?utm_source=chatgpt.com)

另外，**不要急着设 `QUOTA UNLIMITED`**。对于生产环境，我更建议从 `2000M → 5000M` 或 `10000M` 这样有控制地增加。
