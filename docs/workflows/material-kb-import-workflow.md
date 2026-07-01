# Material KB Import Workflow

> **版本**: 1.0 (`v0.3.76`)  
> **创建时间**: 2026-07-01  
> **入口命令**: [`docs/commands/material-kb-import-command.md`](../commands/material-kb-import-command.md)  
> **入口脚本**: `scripts/material_to_kb.py`

---

## 工作流目标

让用户以后可以只说：

```text
解读并入库这个材料：
<公众号链接 / 普通网页链接 / YouTube 链接 / PDF / HTML / Markdown / TXT>
```

或批量：

```text
批量解读并入库这些材料：
<materials.txt>
```

agent 先使用 `scripts/material_to_kb.py` 判断材料类型，再路由到仓库已经存在且稳定的导入能力。没有稳定路线的类型必须返回 `BLOCKED_UNSUPPORTED`，不能临时拼一个半成品抓取器。

---

## Step 0: 仓库检查

```bash
git status --short
git branch --show-current
git fetch origin main --tags
python3 scripts/check_task_preflight.py --planned-tag v0.3.76-unified-material-kb-import-router --classify-dirty --json
```

要求：

- 当前分支是 `main`。
- 没有非本任务 tracked dirty 改动。
- 不 `git reset`。
- 不 `git add -A`。
- 不删除未跟踪 artifact。

---

## Step 1: dry-run 路由

单条：

```bash
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run
```

批量：

```bash
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
```

检查报告中的：

- `inferred_type`
- `route`
- `status`
- `failure_reason`
- 是否存在 `BLOCKED_UNSUPPORTED`
- 是否有 `BLOCKED_FETCH_FAILED` 或 `BLOCKED_INCOMPLETE_TEXT`

dry-run 不应写入 KB 条目。

---

## Step 2: import

只有 dry-run 结果满足预期时才执行：

```bash
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
```

或：

```bash
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

当前 v0.3.76 的真实导入路线只有：

- 微信公众号 URL
- 微信公众号 HTML / Markdown / TXT

YouTube、普通网页、PDF 如果没有仓库内稳定脚本，必须保留 `BLOCKED_UNSUPPORTED`。

---

## Step 3: 统一报告

每次运行都会写：

```text
reports/material_import_YYYYMMDD_HHMMSS.md
reports/material_import_YYYYMMDD_HHMMSS.json
```

批量导入时，一个 input 失败不能中断整批；最终报告必须保留每条 input 的结果。

---

## Step 4: 门禁

如果本次有真实 `IMPORTED`：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

如果没有真实导入：

```bash
python3 -m py_compile scripts/*.py
python3 tests/run_material_router_smoke.py
```

任务收口或版本提交前仍按完整任务门禁执行。

---

## 当前路由表

| inferred_type | 输入 | 路由 | 状态 |
|---|---|---|---|
| `wechat_url` | `mp.weixin.qq.com` / `weixin.qq.com` | `wechat_url_to_kb.py` 或 `wechat_batch_import.py` | 支持 |
| `local_text_article` | `.html` / `.htm` / `.md` / `.markdown` / `.txt` | `wechat_url_to_kb.py` local file mode 或 batch | 支持 |
| `youtube_url` | `youtube.com` / `youtu.be` | 未接入稳定脚本 | `BLOCKED_UNSUPPORTED` |
| `generic_web_url` | 其他 HTTP(S) URL | 未接入稳定脚本 | `BLOCKED_UNSUPPORTED` |
| `pdf_file` | 本地 `.pdf` | 未接入稳定脚本 | `BLOCKED_UNSUPPORTED` |

---

## 停止条件

- 仓库存在明显无关 tracked dirty 改动。
- 下游 WeChat 脚本判断正文不完整。
- `check_kb.py` 或 `check_pages_sync.py` 失败。
- 用户要求的材料类型尚未实现稳定导入路线。
- 需要登录、扫码、cookie 或绕过访问限制才能获取正文。

发生停止时，状态应写为 `BLOCKED_*` 或 `FAILED_*`，并在报告中保留原因。
