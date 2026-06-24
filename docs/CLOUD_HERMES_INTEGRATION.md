# Cloud Hermes 知识库接入说明

> 本文件记录云端 Hermes Agent (Ubuntu VM) 对 `hermes-knowledge-base` 的写入接入规范。
> 适用于在云端环境 (`ubuntu@VM-0-4-ubuntu`) 运行的 Hermes 实例。

## 1. 云端 repo 路径

- **本地路径**：`~/hermes-knowledge-base/`
- **远程 URL**：`https://github.com/conanxin/hermes-knowledge-base.git`
- **默认分支**：`main`
- **关联 Hermes profile**：default (云端主实例)

## 2. 关键约束（硬性）

### 2.1 路径约束

- **不使用 `~/.hermes/wiki/knowledge/` 作为知识库路径**
  - `~/.hermes/wiki/knowledge/` 是 Hermes 内部研究归档目录（10 份 md），命名空间独立
  - 任何 KB 操作必须走 `~/hermes-knowledge-base/`，不得在 `~/.hermes/wiki/knowledge/` 下创建/修改文件
- **不修改 OpenClaw 目录**（`~/.openclaw/`，`~/openclaw-recovery-backups/` 等）

### 2.2 系统组件约束

- 不修改 `~/.hermes/config.yaml` 中的 telegram / gateway / cron / systemd 配置
- 不改 Telegram channel / gateway 进程 / cron jobs / systemd unit
- 不重启 gateway

### 2.3 认证约束

- 不执行 `gh auth refresh`
- 不在 `~/.netrc` / `~/.config/gh/hosts.yml` 写入新 token
- 不修改 `~/.hermes/.env` 中的 token
- **使用现有 token 通过 repo-local proxy 完成 push**

### 2.4 Git 行为约束

- 不 force push
- 不 rebase 共享分支
- 不修改历史 commit
- 每次 commit 必须明确对应一次有边界的导入 / 文档变更

## 3. 导入前必做：同步远端

**开始任何导入前必须执行**：

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
```

- `--ff-only` 强制 fast-forward；任何非 fast-forward 的情况都意味着本地有未推送的 commit 或历史分歧 — 立即停止并报告
- 拉取后必须确认 `git status` 干净、`git log -1` 与 origin/main 一致

## 4. 云端 GitHub 写入路径：repo-local proxy

云端网络环境特殊：**默认 `ALL_PROXY=socks5://127.0.0.1:7898` 环境变量**会触发 git 客户端的 GnuTLS bug（`GnuTLS recv error (-110)`），导致 `git fetch` / `git push` 失败。但 `curl` / `gh api` 走同一代理不受影响。

**解决方案：repo-local git config**（只对当前 KB 仓库生效，不污染全局）：

```bash
cd ~/hermes-knowledge-base
git config --local http.proxy  socks5://127.0.0.1:7898
git config --local https.proxy socks5://127.0.0.1:7898
```

### 4.1 验证配置

```bash
git config --local --get http.proxy
git config --local --get https.proxy
# 预期输出: socks5://127.0.0.1:7898 (两行)
```

### 4.2 验证可达

```bash
git fetch origin                    # 静默 exit 0
git pull --ff-only origin main      # "Already up to date."
git push --dry-run origin main      # "Everything up-to-date"
```

- **如果仍出现 GnuTLS -110**：说明 proxy 端口或 SOCKS 状态变化，先排查 `sing-box` 服务（pid 1751052 / 1751024）健康
- **如果出现 401/403**：token 失效 — 报告，但不执行 `gh auth refresh`

### 4.3 关键区别

| 场景 | 走 proxy 方式 | 状态 |
|---|---|---|
| `curl https://github.com/...` | 默认 `ALL_PROXY` | ✅ 通（OpenSSL） |
| `gh api ...` | 默认 `ALL_PROXY` | ✅ 通 |
| `git fetch` 默认 | 默认 `ALL_PROXY` | ❌ `GnuTLS -110` |
| `git fetch` 配 repo-local proxy | `git config http.proxy` | ✅ 通 |
| `git -c http.proxy=socks5://... fetch` | 单次配置 | ✅ 通（不写入 config） |

## 5. 短命令导入文章的标准流程

**触发短语**（与 `docs/AGENT_COMMANDS.md` 一致）：
- "把这篇文章完整翻译并加入知识库：【URL】"
- "入库并完整翻译：【URL】"
- "加入知识库：【URL】"
- "翻译后入库：【URL】"
- "把这篇文章完整翻译并加入知识库：URL"

**云端执行流程**：

### 5.1 前置同步

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
git status   # 必须干净
```

### 5.2 完整健康检查（按 AGENT_COMMANDS.md 要求执行）

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_pages_sync.py
python3 scripts/check_translation_residue.py
```

**预期**：
- `check_kb.py` → **PASS**（Total items: 23, PASS: 23, FAIL: 0）
- `update_site.py` → **PASS**（5 步 pipeline 全 OK）
- `check_pages_sync.py` → **PASS**（site/ ↔ docs/ byte-identical）
- `check_translation_residue.py` → 可以 **WARNING**，但不能崩溃

### 5.3 硬停止条件

**`check_kb.py` 或 `check_pages_sync.py` FAIL 时必须 hard-stop，不得 commit / push**。

立即停止的标准：
- `check_kb.py` 输出 `STATUS: FAIL` → 立即 `git checkout -- site/data/catalog.json docs/data/catalog.json index/` 回滚 update_site.py 的副作用，然后向用户报告
- `check_pages_sync.py` 显示 site/ 与 docs/ 字节不一致 → 立即 `python3 scripts/sync_pages_docs.py` 重同步，重跑 check；仍失败则停止
- `check_translation_residue.py` 出现 `suspicious_count ≥ 20` → 翻译质量门禁未过，必须修复后重跑

### 5.4 commit 前必检

```bash
git status --short
git diff --stat
```

**commit 前必须确认工作区只包含本次导入相关文件**：
- `content/articles/YYYY-MM-DD-.../` ← 本次新增
- `index/catalog.jsonl`, `index/timeline.md`, `index/tags.md`, `index/authors.md` ← build_index.py 派生
- `site/data/catalog.json` ← export_site_data.py 派生
- `docs/data/catalog.json`, `docs/items/...`, `docs/index.html` ← sync_pages_docs.py 派生
- `reports/...` ← 导入报告（如果走完整报告流）

**禁止 commit**：
- 任何 `~/.hermes/` 下文件
- 任何 `~/.openclaw/` 下文件
- 任何 `templates/` 或 `scripts/` 改动（除非本次明确要改）
- 任何 `git config` 输出

### 5.5 commit + push

```bash
git add <本次相关文件>
git commit -m "<语义化 commit message>"
git push origin main
```

**commit message 约定**：
- 导入文章：`Import: <slug> (<date>)` 或 `Add import: <slug>`
- 修复：`Fix: <具体修复点>`
- 文档：`Document: <文档主题>`
- 同步：`Sync site/data and docs/ from update_site.py`

## 6. Telegram 通知降级策略

云端 Telegram 通道当前处于离线状态（`httpx.ProxyError: General SOCKS server failure`）— **不依赖 Telegram 通知**。

**降级策略**：
- 报告通过 `~/.hermes/workspace/reports/cloud_hermes_*.md` 落地
- 用户通过 SSH / 本地报告目录查看结果
- 如 Telegram 恢复，按用户要求再启用通知

## 7. 故障排查清单

| 症状 | 检查项 | 修复方式（云端） |
|---|---|---|
| `GnuTLS recv error (-110)` | repo-local proxy 配置 | `git config --local http.proxy socks5://127.0.0.1:7898` |
| `Connection timed out` (github.com:443) | sing-box 是否在跑 | `ps -p 1751052` |
| `401 Unauthorized` push | token 失效 | **不修**，报告 |
| `check_kb.py FAIL` | 哪个 article 没过 | 看输出定位，重写 metadata 或文件 |
| `check_pages_sync.py FAIL` | site/ vs docs/ 不一致 | 重跑 `python3 scripts/sync_pages_docs.py` |
| `git pull` non-fast-forward | 本地有未推送 commit | `git log --oneline origin/main..HEAD` 看哪些 commit 需 push |
| 工作区被 `update_site.py` 搞脏 | 想恢复 | `git checkout -- site/data/catalog.json docs/data/catalog.json index/` |

## 8. 与本地 Hermes 协作的边界

- **本地 Hermes**（Mac/PC）走全局 git config，无需 SOCKS 代理
- **云端 Hermes**（Ubuntu VM）走 repo-local proxy，两边共享同一 GitHub 仓库
- **冲突处理**：先 push 的赢 — 后 push 的必须 `git pull --rebase`（云端用 `--ff-only` 失败时手动 rebase）
- **命名空间隔离**：本地与云端 Hermes 都遵循 `docs/AGENT_COMMANDS.md` 的短命令语义

## 9. 变更历史

| 日期 | 变更 | 提交人 |
|---|---|---|
| 2026-06-24 | 初版：云端写入接入规范 | Hermes Agent (云端) |
