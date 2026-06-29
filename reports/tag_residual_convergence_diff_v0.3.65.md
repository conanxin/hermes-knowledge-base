diff --git a/README.md b/README.md
index d36d7a3..69457aa 100644
--- a/README.md
+++ b/README.md
@@ -184,7 +184,7 @@ hermes-knowledge-base/
 ├── scripts/                     # 自动化（质量门禁 / 构建 / 同步 / 桥接 / 诊断）
 ├── templates/                   # 模板（prompts / metadata / notes …）
 ├── reports/                     # 每次任务的运行报告
-├── docs/                        # 完整手册（GitHub Pages 发布目录）
+├── docs/                        # 手册目录 + GitHub Pages 发布目录
 │   ├── AGENT_COMMANDS.md        #   - Agent 命令总纲
 │   ├── TAXONOMY.md              #   - 字段与类型 schema
 │   ├── RELEASES.md              #   - 发布索引 + 推荐下一版
@@ -201,12 +201,11 @@ hermes-knowledge-base/
 │   ├── releases/                #   - 逐版本的 release notes
 │   ├── items/                   #   - 已生成的详情页快照（生成产物）
 │   └── data/                    #   - catalog / index 产物
-├── site/                        # 开发面；和 docs/ 的发布面字节级一致
-├── docs/                        # GitHub Pages 发布目录（与 site/ 镜像）
-└── site/                        # 开发、调试、本地预览
+├── site/                        # 本地开发/预览面；与 docs/ 镜像
+└── 发布：site/ ↔ docs/ 必须字节级一致，由 scripts/check_pages_sync.py 校核
 ```
 
-发布链路上 `site/` ↔ `docs/` 必须字节级一致；改任意一边都要 `cp` 另一边，并由 `scripts/check_pages_sync.py` 校核。
+> `docs/` 同时承担两个角色：(a) 手册/工作流文档的源；(b) GitHub Pages 的发布面。`site/` 是开发、调试、本地预览（`python3 -m http.server 8000 -d site`）的镜像面。任何一边改动都要在另一边 `cp` 镜像，并由 `scripts/check_pages_sync.py` 校验一致性。
 
 ## 10. Agent 操作边界
 
diff --git a/content/articles/2026/2026-06-24-how-i-write-andrew-stanton/metadata.yaml b/content/articles/2026/2026-06-24-how-i-write-andrew-stanton/metadata.yaml
index 216a17a..11a4dfb 100644
--- a/content/articles/2026/2026-06-24-how-i-write-andrew-stanton/metadata.yaml
+++ b/content/articles/2026/2026-06-24-how-i-write-andrew-stanton/metadata.yaml
@@ -24,18 +24,15 @@ tags:
 - David Perell
 - How I Write
 - Pixar
-- 皮克斯
 - 讲故事
 - 剧本写作
 - animation
-- 动画
 - 海底总动员
 - 玩具总动员
 - Steve Jobs
 - John Lasseter
 - Brain Trust
 - creative process
-- 创作过程
 - writing
 - storytelling
 word_count:
diff --git a/content/articles/2026/2026-06-25-conan-harvard-commencement-2026/metadata.yaml b/content/articles/2026/2026-06-25-conan-harvard-commencement-2026/metadata.yaml
index 4c7da15..26ad1c1 100644
--- a/content/articles/2026/2026-06-25-conan-harvard-commencement-2026/metadata.yaml
+++ b/content/articles/2026/2026-06-25-conan-harvard-commencement-2026/metadata.yaml
@@ -27,16 +27,12 @@ topics:
 tags:
   - "Conan O'Brien"
   - "哈佛"
-  - "毕业演讲"
   - "2026"
   - "Humility"
   - "Pivot"
   - "Luck"
   - "Community"
   - "算法自恋"
-  - "自我认知"
-  - "成功学"
-  - "政治讽刺"
   - "特朗普"
   - "AI"
   - "Walt Whitman"
diff --git a/content/articles/2026/2026-06-27-emerson-compensation/metadata.yaml b/content/articles/2026/2026-06-27-emerson-compensation/metadata.yaml
index b9a1b37..6e2e5fa 100644
--- a/content/articles/2026/2026-06-27-emerson-compensation/metadata.yaml
+++ b/content/articles/2026/2026-06-27-emerson-compensation/metadata.yaml
@@ -34,12 +34,6 @@ tags:
   - philosophy
   - 19th-century
   - ralph-waldo-emerson
-  - 爱默生
-  - 超验主义
-  - 道德哲学
-  - 因果报应
-  - 补偿
-  - 美国文学
 topics:
   - 道德补偿原则
   - 善恶因果的对等
diff --git a/content/articles/2026/2026-06-29-orwell-foundation-why-i-write/metadata.yaml b/content/articles/2026/2026-06-29-orwell-foundation-why-i-write/metadata.yaml
index 5a70360..1ae69a9 100644
--- a/content/articles/2026/2026-06-29-orwell-foundation-why-i-write/metadata.yaml
+++ b/content/articles/2026/2026-06-29-orwell-foundation-why-i-write/metadata.yaml
@@ -18,7 +18,6 @@ topics:
 - 奥威尔
 tags:
 - Orwell
-- 奥威尔
 - 散文
 - 写作动机
 - 政治写作
diff --git a/docs/AGENT_COMMANDS.md b/docs/AGENT_COMMANDS.md
index 1339e5a..fa63333 100644
--- a/docs/AGENT_COMMANDS.md
+++ b/docs/AGENT_COMMANDS.md
@@ -100,6 +100,21 @@ python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name
 | **PASS_WITH_WARNINGS** | 仅当 warning 为已知非阻断项（如 v0.3.36 known duplicate）时可继续，并在报告中记录 |
 | **FAIL** | **立即停止**，不得继续导入、不得 update_site、不得 commit/push |
 
+### Preflight 因非本任务历史报告 dirty 失败（v0.3.66+）
+
+如果 preflight FAIL 的**唯一**原因是 `Working tree dirty:`，且 dirty 条目仅来自**历史 `reports/*.md` 的外部 SHA 回填**（通常是上一次别 session 留下的字段补全），不得：
+
+- ❌ 自行 `git checkout -- <file>` / `git restore <file>` 丢弃
+- ❌ 把这些历史 reports 一并 `git add` 夹带到本任务的 commit / tag 中
+- ❌ 假装工作树干净
+
+应：
+
+- ✅ 在报告中明确记录 dirty 文件路径与来源（pre-existing / 外部 session）
+- ✅ 询问用户或使用 v0.3.66 新增的 `python3 scripts/check_task_preflight.py --classify-dirty --json` 模式（仅在全部 dirty 归类为 EXTERNAL 时降级为 PASS_WITH_WARNINGS，且**绝不**自动 stage / restore / commit）
+- ✅ 在本任务 commit 中 per-file `git add`，只携带本任务明确产出的文件
+- ✅ 后续任务以同样纪律处理（per-task 自报 dirty 来源，不假定继承前序任务）
+
 ---
 
 ## 导入文章流程
diff --git a/reports/v0.3.64_legacy_collections_cleanup_report_20260629.md b/reports/v0.3.64_legacy_collections_cleanup_report_20260629.md
index 9077c14..68c73e9 100644
--- a/reports/v0.3.64_legacy_collections_cleanup_report_20260629.md
+++ b/reports/v0.3.64_legacy_collections_cleanup_report_20260629.md
@@ -27,7 +27,7 @@
 | 项 | 值 |
 |----|-----|
 | **基线 Commit** | `7fff346` |
-| **新 Commit** | 待完成 |
+| **新 Commit** | `0e588c4` |
 | **Tag** | `v0.3.64-legacy-collections-cleanup` |
 | **处理方式** | B（迁移） |
 | **迁移目录数** | 4 |
diff --git a/scripts/check_task_preflight.py b/scripts/check_task_preflight.py
index be541f3..b6afaf3 100755
--- a/scripts/check_task_preflight.py
+++ b/scripts/check_task_preflight.py
@@ -5,10 +5,38 @@ Usage:
     python3 scripts/check_task_preflight.py
     python3 scripts/check_task_preflight.py --planned-tag v0.3.38-task-name
     python3 scripts/check_task_preflight.py --allow-warnings --planned-tag v0.3.38-task-name
+    python3 scripts/check_task_preflight.py --classify-dirty          # see working-tree dirty buckets
+    python3 scripts/check_task_preflight.py --classify-dirty --json  # machine-readable
 
 Exit codes:
     0 - PASS or PASS_WITH_WARNINGS (with --allow-warnings)
     1 - FAIL (repo dirty, tag exists, version conflict, etc.)
+
+Flags:
+    --planned-tag NAME         Verify the planned tag is unused and the minor matches recommended.
+    --allow-warnings           Treat PASS_WITH_WARNINGS as an acceptable end state (exit 0).
+    --classify-dirty           Instead of FAILing on dirty tree, classify the dirty entries and
+                               downgrade to PASS_WITH_WARNINGS if every dirty entry is in an
+                               external / non-task bucket (e.g. pre-existing reports/*.md SHA
+                               backfills from another session). Default strict behavior is
+                               preserved: omitting this flag still FAILs on any dirty tree.
+    --skip-heavy-checks        Skip scripts/check_tracks.py (saves ~10s).
+    --json                     Emit machine-readable JSON.
+
+Notes (v0.3.66+):
+    - --classify-dirty NEVER auto-stages, auto-restores, auto-commits, or auto-`git add`s
+      anything. It only classifies.
+    - The default strict gate is preserved as the recommended gate for new agents; --classify-dirty
+      is for triage and audit trails only.
+    - When --classify-dirty is set and all dirty entries are classified as "external / non-task"
+      (e.g. pre-existing dirty files under reports/ that this task will not stage), the gate
+      emits PASS_WITH_WARNINGS rather than FAIL.
+    - When --classify-dirty is set AND any dirty file looks task-relevant (e.g. README.md,
+      scripts/*.py, content/*, site/*, docs/*), the gate falls back to FAIL to mirror the
+      strict default — operating on dirty work that looks self-introduced is unsafe under
+      this flag.
+    - JSON output includes a `dirty_classification` block when --classify-dirty is set, with
+      per-entry buckets.
 """
 
 import argparse
@@ -71,6 +99,141 @@ def parse_minor_version(tag_name):
     return None
 
 
+# Paths whose modifications are considered "self-introduced / task-relevant" by the
+# --classify-dirty heuristic. If any dirty entry hits one of these prefixes, the gate does
+# NOT downgrade to PASS_WITH_WARNINGS — it stays at strict FAIL.
+_TASK_RELEVANT_PATH_PREFIXES = (
+    "README.md",
+    "CLAUDE.md",
+    "CHANGELOG.md",
+    "DESIGN_RATIONALE.md",
+    "content/",
+    "site/",
+    "docs/",
+    "scripts/",
+    "templates/",
+    "inbox/",
+)
+
+# Heuristic: a historical "reports/*.md SHA backfill" pattern is a single-line edit where
+# the diff replaces a `待完成` / `TBD` / `pending` placeholder with a 7-40 char hex SHA, often
+# in the table row that carries `| **新 Commit** | ...` style content. We use a simple count
+# of SHA-shaped tokens added across `git diff <path>` to flag external SHA backfills.
+_SHA_TOKEN_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
+_BACKFILL_PLACEHOLDER_RE = re.compile(r"待完成|TBD|PENDING|pending|\.\.\.")
+
+
+def classify_dirty_entries(status_output):
+    """Classify porcelain git status --short output.
+
+    Returns a dict with:
+      - entries:                list of {status, path, bucket} (one per status line)
+      - counts_by_bucket:       {bucket: int}
+      - has_self_introduced:    bool (True iff any entry is "task-relevant")
+      - summary:                human-readable summary string
+    Buckets:
+      - "staged"             : porcelain XY in {M,A,D,R,C} and uppercase stage letter
+      - "unstaged"           : porcelain Y in lowercase (index modification / deletion) but X is space
+      - "untracked"          : "??" prefix
+      - "report-external-sha-backfill" : under reports/*.md path AND diff looks like a SHA backfill
+      - "report-other"       : under reports/*.md path but not classified as SHA backfill
+      - "other-external"     : anything not covered by the above (probably task-irrelevant too)
+      - "task-relevant"      : path matches _TASK_RELEVANT_PATH_PREFIXES
+    Note: an entry's bucket is the most-specific classification. An entry under reports/*.md
+    whose diff also matches the SHA-backfill heuristic gets bucket="report-external-sha-backfill",
+    NOT "report-other". A README.md entry is always bucket="task-relevant".
+    """
+    entries = []
+    counts = {}
+    has_self = False
+
+    for line in (status_output or "").splitlines():
+        line = line.rstrip()
+        if not line:
+            continue
+        # Porcelain v1 format: XY<SP>PATH (where <SP> is a literal space, not whitespace)
+        if len(line) < 4 or line[2] != " ":
+            # Skip malformed lines; shouldn't happen in normal `git status --short` output.
+            continue
+        x = line[0]
+        y = line[1]
+        path = line[3:].strip()
+        # For renames/copies, take the right side ("path1 -> path2"), take path2.
+        if " -> " in path:
+            path = path.split(" -> ", 1)[1]
+        path = path.strip('"')
+
+        # Bucket assignment: most-specific first.
+        bucket = None
+
+        # 1. Path-prefix based: README / scripts / content / ... → always task-relevant.
+        if any(path == p or path.startswith(p) for p in _TASK_RELEVANT_PATH_PREFIXES):
+            bucket = "task-relevant"
+
+        # 2. reports/*.md + SHA backfill heuristic → external SHA backfill
+        if bucket is None and path.startswith("reports/") and path.endswith(".md"):
+            # Run a small diff to count SHA-token insertions. This is best-effort; if git
+            # fails for any reason, fall back to "report-other".
+            try:
+                diff_out = subprocess.run(
+                    ["git", "diff", "--", path],
+                    capture_output=True, text=True, check=False,
+                ).stdout
+                added_sha_hits = 0
+                removed_placeholder_hits = 0
+                for dline in diff_out.splitlines():
+                    if dline.startswith("+") and not dline.startswith("+++"):
+                        added_sha_hits += len(_SHA_TOKEN_RE.findall(dline))
+                    elif dline.startswith("-") and not dline.startswith("---"):
+                        removed_placeholder_hits += len(_BACKFILL_PLACEHOLDER_RE.findall(dline))
+                if added_sha_hits >= 1 and removed_placeholder_hits >= 1:
+                    bucket = "report-external-sha-backfill"
+                else:
+                    bucket = "report-other"
+            except Exception:
+                bucket = "report-other"
+
+        # 3. porcelain state-tag buckets — only kicks in when no specific bucket was set
+        #    by the path-prefix / reports-SHA-backfill logic above. Every branch must guard
+        #    with `bucket is None` so a previously-set bucket (task-relevant / report-*) is
+        #    never silently overwritten by the porcelain fallback.
+        if bucket is None:
+            if x == "?" and y == "?":
+                bucket = "untracked"
+            elif x != " " and x != "?":
+                bucket = "staged"
+            elif y != " " and y != "?":
+                bucket = "unstaged"
+            else:
+                bucket = "other-external"
+
+        # has_self_introduced: task-relevant always counts.
+        if bucket == "task-relevant":
+            has_self = True
+
+        entries.append({
+            "status": line[:2],
+            "path": path,
+            "bucket": bucket,
+        })
+        counts[bucket] = counts.get(bucket, 0) + 1
+
+    return {
+        "entries": entries,
+        "counts_by_bucket": counts,
+        "has_self_introduced": has_self,
+        "summary": _format_summary(counts, has_self),
+    }
+
+
+def _format_summary(counts, has_self):
+    if not counts:
+        return "working tree clean"
+    parts = [f"{bucket}={n}" for bucket, n in sorted(counts.items())]
+    sigil = "SELF" if has_self else "EXTERNAL"
+    return f"{sigil}: " + ", ".join(parts)
+
+
 def get_recommended_minor():
     """Get recommended next minor from check_release_tags.py."""
     status, output = run_check_script("scripts/check_release_tags.py")
@@ -85,6 +248,17 @@ def main():
     parser = argparse.ArgumentParser(description="Task preflight checker")
     parser.add_argument("--planned-tag", help="Planned version tag for the task")
     parser.add_argument("--allow-warnings", action="store_true", help="Allow PASS_WITH_WARNINGS status")
+    parser.add_argument(
+        "--classify-dirty",
+        action="store_true",
+        help=(
+            "v0.3.66+: instead of FAILing on a dirty working tree, classify each dirty entry "
+            "and downgrade to PASS_WITH_WARNINGS when every entry is in an external bucket "
+            "(e.g. pre-existing reports/*.md SHA backfills from another session). When any entry "
+            "is task-relevant (README.md, scripts/*, content/*, site/*, docs/*), the gate "
+            "still FAILs to mirror strict default. Never auto-stages or auto-restores."
+        ),
+    )
     parser.add_argument("--skip-heavy-checks", action="store_true", help="Skip heavy checks like check_tracks.py")
     parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
     args = parser.parse_args()
@@ -105,11 +279,43 @@ def main():
         sys.exit(1)
     results["checks"]["git_repo"] = "PASS"
 
-    # 2. Check git status
-    status_output = run_git("status", "--short", check=False)
+    # 2. Check git status — strict default: any dirty → FAIL.
+    #    v0.3.66+: --classify-dirty downgrades to PASS_WITH_WARNINGS iff every entry is
+    #    classified as external / non-task; it NEVER auto-stages anything.
+    #    NB: do NOT use run_git(..., check=False).strip() here, because .strip() removes the
+    #    leading space of ` M` (unstaged modification) porcelain entries, silently corrupting
+    #    the first line of every dirty tree. We want raw status output, trailing newline excepted.
+    try:
+        _status_proc = subprocess.run(
+            ["git", "status", "--short"],
+            capture_output=True, text=True, check=False,
+        )
+        status_output = _status_proc.stdout.rstrip("\n")
+    except FileNotFoundError:
+        status_output = None
     if status_output:
-        results["errors"].append(f"Working tree dirty:\n{status_output}")
-        results["status"] = "FAIL"
+        if args.classify_dirty:
+            classification = classify_dirty_entries(status_output)
+            results["checks"]["git_status"] = "PASS_WITH_WARNINGS"
+            results["checks"]["git_status_classification"] = classification["summary"]
+            results["dirty_classification"] = classification
+            if classification["has_self_introduced"]:
+                results["errors"].append(
+                    "Working tree dirty (classify mode): SELF-introduced files present.\n"
+                    + status_output
+                    + "\nClassification: " + classification["summary"]
+                )
+                results["status"] = "FAIL"
+            else:
+                results["warnings"].append(
+                    "Working tree dirty but all entries are EXTERNAL (pre-existing / not this task). "
+                    "Classified: " + classification["summary"]
+                    + "\n" + status_output
+                    + "\nNo auto-stage, no auto-restore, no auto-commit. Carry on cautiously."
+                )
+        else:
+            results["errors"].append(f"Working tree dirty:\n{status_output}")
+            results["status"] = "FAIL"
     else:
         results["checks"]["git_status"] = "PASS"
 
