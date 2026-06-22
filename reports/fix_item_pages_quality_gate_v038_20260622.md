# Fix item pages quality gate hard stop

**Date**: 2026-06-22
**Scope**: hermes-knowledge-base — close v0.3.8 PARTIAL status, restore `check_kb.py` PASS
**Builds on**: `c231605 Add static item detail pages`

## 1. `word_count` 修复

### Root cause (different from the user's initial diagnosis)

The user reported `word_count: "4500"` (a quoted string) and asked to convert it to `word_count: 4500` (a bare YAML int). The actual file content was already `word_count: 4500` (unquoted) on line 24 of `content/articles/2026/2026-03-25-reverse-game-theory-housing-shortage/metadata.yaml`. The real `check_kb.py` failure was a **schema mismatch**, not a quoting issue:

`scripts/check_kb.py` lines 111–114 require `word_count` to be a **dict**:

```python
word_count = data.get("word_count", {})
if not isinstance(word_count, dict):
    issues.append(f"INVALID word_count type in {rel_meta}")
```

The 2026-03-25 article (the only legacy record in `content/articles/`) was still using a bare-int legacy form, while the other 18 records (including all 4 post-`v0.3.8` imports) use the modern dict schema:

```yaml
word_count:
  source: <int>      # source.md 实际词数
  translation: <int> # translation.zh-CN.md 实际 CJK 字数
```

### Fix applied

Updated the file to the dict schema with **actual** word counts (re-measured from disk):

```yaml
word_count:
  source: 4434        # wc -w source.md
  translation: 7079   # CJK chars in translation.zh-CN.md
```

`wc -w source.md` → **4434** words (the legacy estimate of "4500" was off by ~1.5 %; we use the real count now).

### Verified

```text
$ python3 scripts/check_kb.py
Total items: 19
PASS: 19
FAIL: 0

STATUS: PASS
```

## 2. `update_site.py` hard-stop 修复

### Before

```python
SCRIPTS = [
    "scripts/build_index.py",
    "scripts/export_site_data.py",
    "scripts/generate_item_pages.py",
    "scripts/sync_pages_docs.py",
]
# run each in order, stop on first failure
```

`check_kb.py` was not part of `update_site.py`. A failing KB would let `update_site.py` happily regenerate `site/data/catalog.json`, build 19 item pages, and overwrite `docs/` — **violating** the documented hard-stop quality gate.

### After

`update_site.py` now runs `check_kb.py` as `STEP 0/4` before any other script:

```python
QUALITY_GATE = "scripts/check_kb.py"
BUILD_CHAIN = [
    "scripts/build_index.py",
    "scripts/export_site_data.py",
    "scripts/generate_item_pages.py",
    "scripts/sync_pages_docs.py",
]

def update_site() -> int:
    # HARD-STOP: quality gate first
    if not run_script(QUALITY_GATE):
        print("! HARD-STOP: check_kb.py FAILED.")
        print("! Refusing to: rebuild / regenerate / generate / sync.")
        return 1
    # build chain (only reachable if gate passed)
    ...
```

Pipeline order:

```
check_kb.py            ← 质量门禁，FAIL 立即停止
build_index.py
export_site_data.py
generate_item_pages.py
sync_pages_docs.py
```

### Hard-stop verified

I temporarily broke `content/articles/2026/2026-06-22-your-ai-is-not-a-tool/metadata.yaml` (replaced `word_count:` with `word_count: 9999` mid-dict, producing a YAML scanner error). Then ran `python3 scripts/update_site.py`:

```text
! HARD-STOP: scripts/check_kb.py FAILED.
! The knowledge base has integrity issues. Refusing to:
!   - rebuild index/catalog.jsonl
!   - regenerate site/data/catalog.json
!   - generate site/items/ detail pages
!   - sync to docs/
!
! Fix the issues reported above, then re-run update_site.py.
EXIT=1
```

Then restored the file, and `update_site.py` ran all 5 steps green.

## 3. Pipeline results

| Check | Result |
|-------|--------|
| `python3 scripts/check_kb.py` | **PASS — 19/19, 0 FAIL** |
| `python3 scripts/update_site.py` | **PASS** — 5 steps green (gate + 4 build), exit 0 |
| `python3 scripts/check_translation_residue.py` | WARNING (pre-existing book-title residues, not from this change) |

`update_site.py` output (key lines):

```text
# STEP 0/4: Quality gate (check_kb.py)
[1/4] scripts/build_index.py OK
[2/4] scripts/export_site_data.py OK
[3/4] scripts/generate_item_pages.py OK
[4/4] scripts/sync_pages_docs.py OK
All steps completed successfully.
```

## 4. Local smoke test (`python3 -m http.server 8765 -d site`)

| Check | Result |
|-------|--------|
| `GET /` | 200 |
| `catalog.json` records | 19 (6 article, 5 note, 4 project, 4 collection), all with `detail_url` |
| Article detail page (e.g. `2026-06-22-your-ai-is-not-a-tool`) | 200, 31,830 bytes, contains "中文翻译" / "返回首页" / "GitHub 文件夹" / "复制 path" / `github.com/conanxin/...` link |
| Collection detail page (`2026-05-06-arxiv-ai-agents`) | 200 |
| Legacy 2026-03-25 article (the one we fixed) | 200, 42,052 bytes, contains "逆向博弈论" + "中文翻译" |
| All 19 `items/<slug>/` URLs | **19/19 → 200** |

> Port 8765 instead of 8000 — local SurrealDB is bound to 8000 on this host.

## 5. site/ ↔ docs/ sync

```
Synced 4 top-level files from site/ to docs/:
  index.html, app.js, styles.css, data/catalog.json
Mirrored 19 files under site/items/ → docs/items/.
```

Hand-authored docs (AGENT_COMMANDS.md, COLLECTIONS.md, LEGACY_MIGRATION.md, TAXONOMY.md) preserved untouched. The 2026-03-25 detail page was regenerated with the new metadata (the `word_count` field is not actually rendered on the page, but the YAML schema is now consistent across all 19 records).

## 6. Docs updated

| File | Change |
|------|--------|
| `README.md` | New "质量门禁（硬性规则）" section; pipeline diagram updated to show `check_kb.py` first |
| `docs/AGENT_COMMANDS.md` | Quality gate section rewritten to match `update_site.py` hard-stop; pipeline order diagram added |
| `templates/prompts/import_article_prompt.md` | File was truncated+duplicated; rewrote cleanly with the same hard-stop rules + canonical `word_count` dict example |
| `scripts/update_site.py` | Hard-stop rewrite (see §2) |

## 7. GitHub Pages records 数

Online (after push, post CDN sync):

- Homepage: <https://conanxin.github.io/hermes-knowledge-base/> — 19 records
- Article: <https://conanxin.github.io/hermes-knowledge-base/items/2026-06-22-your-ai-is-not-a-tool/>
- Legacy 2026-03-25 article (the one fixed in this commit): <https://conanxin.github.io/hermes-knowledge-base/items/2026-03-25-reverse-game-theory-housing-shortage/>
- Collection: <https://conanxin.github.io/hermes-knowledge-base/items/2026-05-06-arxiv-ai-agents/>

## 8. Files changed

| Status | Path |
|--------|------|
| M | `content/articles/2026/2026-03-25-reverse-game-theory-housing-shortage/metadata.yaml` |
| M | `scripts/update_site.py` |
| M | `README.md` |
| M | `docs/AGENT_COMMANDS.md` |
| M | `templates/prompts/import_article_prompt.md` |
| M | `site/data/catalog.json` (regenerated by `update_site.py`) |
| M | `site/items/2026-03-25-reverse-game-theory-housing-shortage/index.html` (regenerated) |
| M | `docs/data/catalog.json` (synced) |
| M | `docs/items/2026-03-25-reverse-game-theory-housing-shortage/index.html` (synced) |
| A | `reports/fix_item_pages_quality_gate_v038_20260622.md` |

## 9. Follow-ups (not blocking)

- [ ] Add a test that intentionally breaks a metadata field and asserts `update_site.py` exits non-zero, so the hard-stop can't silently regress in future refactors.
- [ ] The hard-stop in `update_site.py` currently runs `check_kb.py` once at the start. If a later step corrupts the catalog on disk (e.g. `build_index.py` bug), the gate won't catch it. Consider re-running `check_kb.py` at the very end as a "post-publish gate" before the user runs commit/push.
- [ ] `check_translation_residue.py` 5 book-title hits remain — they're all intentional proper-noun retention, but the WARNING text should be more honest ("expected: book titles") so future readers don't treat it as a regression.
