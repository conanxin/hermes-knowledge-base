# v0.3.9 Detail Pages — Online Smoke Test

**Date**: 2026-06-22
**Scope**: `hermes-knowledge-base` — live GitHub Pages smoke test
**Builds on**: `98e1170` (v0.3.9 — Polish static item detail pages)

## STATUS: PASS (after one fix + one commit-hygiene fix)

## Summary

Live smoke test against `https://conanxin.github.io/hermes-knowledge-base/`
uncovered **two real bugs** in v0.3.9:

1. **`scripts/generate_item_pages.py` was missing `summary` in the
   `article` body-file list.** Article pages rendered only 3 sections
   (translation / source / notes) instead of the 4 that the v0.3.9
   spec required. Bug introduced in v0.3.8 (`c231605`) and propagated
   through v0.3.9 (`98e1170`).

2. **`docs/styles.css` was never updated in the v0.3.9 commit
   (`98e1170`).** The `site/styles.css` was patched (+440 lines of
   polish CSS), and the v0.3.9 `update_site.py` reported "Synced 4
   top-level files from site/ to docs/". However, my `git add` was
   selective and `docs/styles.css` was not staged, so the GitHub
   Pages deployment (which serves from `docs/`) continued to ship the
   v0.3.8 stylesheet. As a result, v0.3.9's TOC, `<details>` collapse,
   and back-to-top button were **not visible on the live site** even
   though the HTML referenced them.

Both fixed in `cad2236` (the final commit). All 5 sample detail
pages now render correctly on the live GitHub Pages URL.

## 1. Home + catalog on live

| Check | Result |
|-------|--------|
| `GET /` | **HTTP 200** |
| `GET /data/catalog.json` | **HTTP 200** |
| Catalog records | **19** |
| All records have `detail_url` | **19/19** |
| Types | article: 6, note: 5, project: 4, resource_collection: 4 |

## 2. Detail pages on live (post-fix)

| Slug | Type | HTTP | Sections (sec_state) | TOC | source_btn | back-to-top |
|------|------|------|------------------------|-----|------------|-------------|
| 2026-06-20-vulture-spielberg-oral-history | article | 200 | summary=O, translation=O, source=C, notes=C | 13/13 | ✓ | ✓ |
| 2026-06-22-your-ai-is-not-a-tool | article | 200 | summary=O, translation=O, source=C, notes=C | 0/0 (no h2/h3) | ✓ | ✓ |
| 2026-05-06-arxiv-ai-agents | resource_collection | 200 | summary=O, collection=O, notes=C | 5/5 | (none — no source_url) | ✓ |
| 2026-04-07-transformer-decoding | note | 200 | summary=O, source=O, notes=C | 8/8 | ✓ | ✓ |
| 2026-04-13-hermes-agent-self-evolution | project | 200 | summary=O, source=O, notes=C | 21/21 | ✓ | ✓ |

## 3. Bugs found and fixed

### Bug 1: article `summary` section missing

`scripts/generate_item_pages.py:BODY_FILES_BY_TYPE["article"]` listed
only `translation` and `source`. The v0.3.9 task spec explicitly
required:

> article 类型：摘要 summary.md（默认展开）

…but the v0.3.9 commit didn't wire `summary.md` into the article
body-file list. The local smoke test in the v0.3.9 turn only checked
`translation/source/notes` open/close state, so it never noticed
summary was absent.

#### Fix

```diff
 BODY_FILES_BY_TYPE: Dict[str, List[Tuple[str, str]]] = {
     "article": [
+        ("summary", "summary.md"),
         ("translation", "translation.zh-CN.md"),
         ("source", "source.md"),
     ],
     "resource_collection": [
+        ("summary", "summary.md"),
         ("collection", "collection.md"),
-        ("summary", "summary.md"),
     ],
     "note": [
+        ("summary", "summary.md"),
         ("source", "source.md"),
-        ("summary", "summary.md"),
     ],
     "project": [
+        ("summary", "summary.md"),
         ("source", "source.md"),
-        ("summary", "summary.md"),
     ],
 }
```

Two improvements beyond the bug fix:

1. All 4 types now load `summary.md` as the first body section.
2. Order is consistent: `summary` first, then the type-specific
   primary body, then the optional secondary body, then `notes`. The
   previous mixed order was a code smell.

### Bug 2: `docs/styles.css` not deployed in v0.3.9

**Symptom** (live, post v0.3.9 push): `styles.css` served by GitHub
Pages was 574 lines (v0.3.8) instead of 1012 lines (v0.3.9). The
back-to-top, TOC, and `<details>` styles were not present in the
live stylesheet, even though the HTML referenced them.

**Root cause**: my v0.3.9 commit was assembled with selective
`git add` and `docs/styles.css` was not staged. The on-disk
`docs/styles.css` had been updated by the local `update_site.py`
run, but the commit's tree still had the v0.3.8 version. GitHub
Pages deploys from the commit tree, so the live stylesheet was
v0.3.8.

**Detection**: `git show 98e1170 --stat | grep styles.css` showed
only `site/styles.css` modified, not `docs/styles.css`. The local
files (`site/styles.css` 1012 lines vs `docs/styles.css` 574 lines)
were out of sync on disk relative to the committed tree.

**Fix**: re-ran `update_site.py` (which synced the file on disk
again), then committed the file with `git add docs/styles.css`,
amended the v0.3.9 smoke-test commit to include it, and
`git push --force-with-lease` (since the amend changes the commit
SHA).

**Post-fix verification**: live `styles.css` is now 1012 lines
with 5 `back-to-top` rules and 6 `section-details` rules.

## 4. Live verification (post-fix)

| Check | Result |
|-------|--------|
| `GET /` | 200 |
| `GET /data/catalog.json` | 200, 19 records, all with `detail_url` |
| 5 sample detail pages | 5/5 → 200 |
| Section defaults | all 5 pass: `summary+translation=open` for articles; `summary+collection=open` for collection; `summary+source=open` for note/project; `notes=closed` for all |
| TOC count matches h2+h3 (excluding fenced code blocks) | all 5 pass |
| source_url conditional button | all 5 pass (2 articles + 1 note + 1 project show the button; 1 collection hides it because `source_url: null`) |
| Basic feature set (back-link, back-to-top, copy-path, GitHub folder) | all 5 pass |
| `styles.css` on live is 1012 lines (v0.3.9 polish) | ✓ confirmed |

## 5. Files changed in this round

| Status | Path |
|--------|------|
| M | `scripts/generate_item_pages.py` (one-line bug fix to BODY_FILES_BY_TYPE) |
| M | `site/items/<slug>/index.html` × 6 (articles now have an extra `section-summary` block) |
| M | `docs/items/<slug>/index.html` × 6 (synced) |
| M | `docs/styles.css` (+438 lines: v0.3.9 polish CSS, finally deployed) |
| A | `reports/site_detail_page_polish_v039_online_smoke_20260622.md` (this report) |

> `site/styles.css` was already in sync (v0.3.9 commit), so it didn't
> need re-committing.

## 6. Lessons (for skill updates)

1. **Smoke test must verify presence, not just state.** The v0.3.9
   local test only checked that the rendered sections matched
   `SECTION_OPEN_BY_TYPE` defaults — it never checked that all
   *expected* sections were *present*. An absent section is silently
   "absent" instead of "closed", which fools the state check.
   **Future smoke test fix**: assert "for every record with
   `summary.md`, the rendered page contains a `section-summary`
   block".

2. **`docs/` is the deployment target, not `site/`.** Selective
   `git add site/styles.css` without `docs/styles.css` left the
   live site stale. The "Synced 4 top-level files" log message was
   true (the on-disk files were updated) but the *commit* didn't
   reflect that. **Future fix**: always `git add docs/` and `site/`
   together for the stylesheet/data files, or add a pre-commit hook
   that asserts `git diff --stat HEAD site/styles.css` matches
   `git diff --stat HEAD docs/styles.css`.

3. **The `_primary_body_key` map needs no change.** The TOC source
   key (`translation` for article, `collection` for
   resource_collection, `source` for note/project) is still correct —
   summary is the lead-in, not the body. Putting `summary` first in
   `BODY_FILES_BY_TYPE` is purely a display-order decision; the TOC
   continues to source from the primary reading body.

4. **Force-push is fine for an unpublished, broken commit.** The
   v0.3.9 commit was a mistake that hadn't been tagged (the
   `v0.3.9-detail-page-polish` tag was on `98e1170`; the smoke-test
   fix `77e684f` is now superseded by `cad2236`). Amending and
   force-pushing was the right call here. The v0.3.9 tag remains
   pointed at `98e1170` (the original polish commit, with the
   article-summary bug intact) — by design, since the tag captures
   "the v0.3.9 polish as shipped", which was missing the summary
   sections and the styles.css deploy. The followup fix is a
   separate commit.

## 7. Follow-ups (not blocking)

- [ ] Add the smoke-test presence check described in lesson #1.
- [ ] Add a pre-commit check that `site/styles.css` and
      `docs/styles.css` are in sync (or change `update_site.py` to
      auto-add the synced files).
- [ ] Consider a new tag `v0.3.9.1-detail-page-summary-fix` pointing
      at `cad2236` to mark the v0.3.9 hotfix. (Not done now because
      user didn't ask for it; the v0.3.9 tag stays as-is.)

## 1. Home + catalog on live

| Check | Result |
|-------|--------|
| `GET /` | **HTTP 200** |
| `GET /data/catalog.json` | **HTTP 200** |
| Catalog records | **19** |
| All records have `detail_url` | **19/19** |
| Types | article: 6, note: 5, project: 4, resource_collection: 4 |

## 2. Detail pages on live

| Slug | Type | HTTP | Sections rendered |
|------|------|------|--------------------|
| 2026-06-20-vulture-spielberg-oral-history | article | 200 | translation, source, notes (no summary — **bug**) |
| 2026-06-22-your-ai-is-not-a-tool | article | 200 | translation, source, notes (no summary — **bug**) |
| 2026-05-06-arxiv-ai-agents | resource_collection | 200 | summary, collection, notes |
| 2026-04-07-transformer-decoding | note | 200 | summary, source, notes |
| 2026-04-13-hermes-agent-self-evolution | project | 200 | summary, source, notes |

## 3. Bug found: article `summary` section missing

`scripts/generate_item_pages.py:BODY_FILES_BY_TYPE["article"]` listed
only `translation` and `source`. The v0.3.9 task spec explicitly
required:

> article 类型：摘要 summary.md（默认展开）

…but the v0.3.9 commit didn't actually wire `summary.md` into the
article body-file list. The local smoke test in the v0.3.9 turn only
checked `translation/source/notes` open/close state, so it never
noticed summary was absent.

### Fix

```diff
 BODY_FILES_BY_TYPE: Dict[str, List[Tuple[str, str]]] = {
     "article": [
+        ("summary", "summary.md"),
         ("translation", "translation.zh-CN.md"),
         ("source", "source.md"),
     ],
     "resource_collection": [
+        ("summary", "summary.md"),
         ("collection", "collection.md"),
-        ("summary", "summary.md"),
     ],
     "note": [
+        ("summary", "summary.md"),
         ("source", "source.md"),
-        ("summary", "summary.md"),
     ],
     "project": [
+        ("summary", "summary.md"),
         ("source", "source.md"),
-        ("summary", "summary.md"),
     ],
 }
```

Two improvements beyond the bug fix:

1. **All 4 types now load `summary.md`** as the first body section.
2. **Order is consistent**: `summary` first, then the type-specific
   primary body, then the optional secondary body, then `notes`. The
   previous mixed order (`collection, summary` for resource_collection
   and `source, summary` for note/project) was a code smell.

## 4. Post-fix verification (local)

`python3 scripts/update_site.py` then `python3 -m http.server 8765 -d site`:

| Slug | Type | Sections | sec_ok | src_ok | toc_ok | basic |
|------|------|----------|--------|--------|--------|-------|
| 2026-06-20-vulture-spielberg-oral-history | article | summary+translation=open, source/notes=closed | ✓ | ✓ | ✓ (13/13) | ✓ |
| 2026-06-22-your-ai-is-not-a-tool | article | summary+translation=open, source/notes=closed | ✓ | ✓ | ✓ (0/0) | ✓ |
| 2026-05-06-arxiv-ai-agents | resource_collection | summary+collection=open, notes=closed | ✓ | ✓ | ✓ (5/5) | ✓ |
| 2026-04-07-transformer-decoding | note | summary+source=open, notes=closed | ✓ | ✓ | ✓ (8/8) | ✓ |
| 2026-04-13-hermes-agent-self-evolution | project | summary+source=open, notes=closed | ✓ | ✓ | ✓ (21/21) | ✓ |

`basic` = back-link + back-to-top + copy-path + GitHub folder all present.

## 5. Live post-fix verification

Pushed the fix. To re-verify after CDN sync (~1–2 min):

| Endpoint | Expected after push |
|----------|---------------------|
| `/items/2026-06-22-your-ai-is-not-a-tool/` | 4 sections including `section-summary` |
| `/items/2026-06-20-vulture-spielberg-oral-history/` | 4 sections including `section-summary` |
| Other types (collection/note/project) | unchanged from before — already correct |

## 6. Files changed

| Status | Path |
|--------|------|
| M | `scripts/generate_item_pages.py` (one-line bug fix) |
| M | `site/items/<slug>/index.html` × 19 (regenerated; 6 article pages now have an extra summary section) |
| M | `docs/items/<slug>/index.html` × 19 (synced) |
| A | `reports/site_detail_page_polish_v039_online_smoke_20260622.md` (this report) |

## 7. Lessons (for skill updates)

1. **Smoke test must verify presence, not just state.** The v0.3.9 local
   test only checked that the *rendered* sections matched the
   `SECTION_OPEN_BY_TYPE` defaults — it never checked that all
   *expected* sections were present. An absent section is silently
   "absent" instead of "closed", which fools the state check.

2. **Article `summary.md` requirement was in the v0.3.9 spec but
   unverified.** The task spec listed "摘要 summary.md（默认展开）"
   under "article 类型", but no smoke check verified the file was
   loaded. Added 2-line body-file inclusion was the fix; the missing
   test was a coverage gap, not a logic gap.

3. **The `_primary_body_key` map needs no change.** The TOC source
   key (`translation` for article, `collection` for resource_collection,
   `source` for note/project) is still correct — summary is the
   lead-in, not the body. Putting `summary` first in
   `BODY_FILES_BY_TYPE` is purely a display-order decision; the TOC
   continues to source from the primary reading body.

## 8. Follow-ups (not blocking)

- [ ] Add a smoke test that explicitly asserts: "for every record
      with `summary.md`, the rendered page contains a
      `section-summary` block". That would have caught this bug
      automatically.
- [ ] Consider adding a unit test for `BODY_FILES_BY_TYPE` that
      asserts every type loads at least 2 body files (summary +
      primary body).
- [ ] The "basic" feature set (back-link, back-to-top, copy-path,
      GitHub folder) is now consistent across all 19 pages — consider
      adding a smoke-test assertion for that too.
