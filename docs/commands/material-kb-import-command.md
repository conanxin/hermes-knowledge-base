# material-kb-import

> **命令名称**: `material-kb-import`  
> **用途**: 给一个 URL 或本地文件，由统一入口判断材料类型，并路由到仓库已有的稳定入库脚本。  
> **Workflow**: [`docs/workflows/material-kb-import-workflow.md`](../workflows/material-kb-import-workflow.md)  
> **入口脚本**: `scripts/material_to_kb.py`  
> **创建时间**: 2026-07-01  
> **任务标签**: `v0.3.76-unified-material-kb-import-router`; `v0.3.77-generic-web-article-import-route`

---

## 最短调用

在 WorkBuddy 里直接说：

```text
解读并入库这个材料：
<URL 或 本地文件>
```

批量：

```text
批量解读并入库这些材料：
<materials.txt>
```

脚本形式：

```bash
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

`--dry-run` 是默认安全模式，不写 KB 条目。只有显式传 `--import` 才会调用下游脚本真实入库。

---

## input-list 格式

每行一个 URL 或本地文件路径：

```text
# comments are skipped
https://mp.weixin.qq.com/s/...
saved-wechat-article.html
notes/article.md

# blank lines are skipped
```

空行和 `#` 开头的行会跳过。

---

## 当前支持状态

| 材料类型 | 匹配规则 | 当前状态 | 路由 |
|---|---|---|---|
| 微信公众号 URL | `mp.weixin.qq.com`, `weixin.qq.com` | 支持 | 单输入走 `scripts/wechat_url_to_kb.py`，多输入走 `scripts/wechat_batch_import.py` |
| 微信公众号 HTML / MD / TXT | `.html`, `.htm`, `.md`, `.markdown`, `.txt` | 支持 | `wechat_url_to_kb.py` local file mode；批量走 `wechat_batch_import.py` |
| YouTube URL | `youtube.com`, `youtu.be` | 当前返回 `BLOCKED_UNSUPPORTED` | 只有仓库未来出现稳定导入脚本后才接入 |
| 普通网页 URL | 其他 `http://` / `https://` | 支持 | `scripts/web_article_to_kb.py` |
| PDF | 本地 `.pdf` | 当前返回 `BLOCKED_UNSUPPORTED` | PDF import/OCR route 尚未接入统一入口 |

统一入口不会临时发明抓取器。没有稳定脚本的类型必须明确返回 `BLOCKED_UNSUPPORTED`，并写入失败原因。v0.3.77 起普通网页 URL 已接入公开 HTTP 抓取路线；该路线不登录、不读 cookie、不绕过 paywall，不完整正文会 hard stop。

---

## 报告

每次运行都会生成两份报告：

```text
reports/material_import_YYYYMMDD_HHMMSS.md
reports/material_import_YYYYMMDD_HHMMSS.json
```

每条 input 记录：

- `input`
- `inferred_type`
- `route`
- `status`
- `title`
- `source_url`
- `kb_article_path`
- `docs_item_path`
- `site_item_path`
- `capture_json_path`
- `route_report_path`
- `failure_reason`

状态值包括：

- `IMPORTED`
- `DRY_RUN_OK`
- `SKIPPED_DUPLICATE`
- `BLOCKED_UNSUPPORTED`
- `BLOCKED_FETCH_FAILED`
- `BLOCKED_INCOMPLETE_TEXT`
- `FAILED_IMPORT`
- `FAILED_GATE`

---

## 门禁

如果 `--import` 产生了真实 `IMPORTED` 条目，统一入口会运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

如果没有真实导入，任务收口只需要轻量检查：

```bash
python3 -m py_compile scripts/*.py
python3 tests/run_material_router_smoke.py
```

---

## 边界

- 不重新实现公众号导入，只复用现有 `wechat_url_to_kb.py` / `wechat_batch_import.py`。
- 不绕过公众号访问限制，不登录、不扫码、不读 cookie。
- 不伪造 YouTube、PDF 的导入能力。
- 普通网页路线只处理公开可访问正文；需要登录、cookie、付费墙或 JS 登录态的页面返回 `BLOCKED_*`。
- 不覆盖已有 `summary.md` / `notes.md`。
- 不删除 KB 条目、item pages 或 assets。
