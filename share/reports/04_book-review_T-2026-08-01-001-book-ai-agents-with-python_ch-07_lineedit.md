# Line-Edit Review — ch-07 "Call Models Safely from Python"

**Task:** T-2026-08-01-001-book-ai-agents-with-python (book: *AI Agents with Python*, ch-07)
**Phase:** line-edit (post dev-fix1)
**Reviewer:** am-review
**Date:** 2026-08-02
**Files audited:** `books/ai-agents-with-python/chapters/ch-07.md` (post-fix1, 1722 words per writer), `books/ai-agents-with-python/style-guide.md`, `books/ai-agents-with-python/bible.md` (ch-07 block), `books/ai-agents-with-python/ledger.md` (ch-07 row).

---

## Summary

**Overall verdict: PASS_WITH_WARN.**

The chapter cleanly passes the line-edit checklist after dev-fix1. Two non-blocking WARNs remain (one paragraph at the 80-word boundary, one copy-edit-pass acronym note that matches the ch-06 ledger pattern). No FAILs. No subtle technical bugs in the credential helper, retry loop, or `Retry-After` parser. The chapter is ready for the whole-book copy-edit pass.

**Verdict counts:** FAIL = 0 | WARN = 2 | LOW = 2

---

## Tests / build run

- **Word count** (prose with inline-code stripped, this reviewer's methodology): **1597 words**. Writer claims 1722 (same methodology, ledger row). The 125-word delta is methodology noise (the writer's count is permissive on link-syntax stripping; both numbers fall in the dispatch's 1548-1894 acceptance band). Independent count 1597 is comfortably inside the band; the chapter is not bloated or short.
- **UTF-8 round-trip:** clean. Encoded → decoded bytes identical. 69 non-ASCII bytes (em dash, curly quotes in test block, en dash in "ch-04").
- **No build required** (markdown chapter).
- **No code execution** (this is a line-edit; runnable checks already verified by dev-fix1 per ledger: TEST-NET-1 demo produces `final bucket=exhausted info=('network', 'timed out')`).

---

## Per-checklist verdicts

### Voice (line-edit focus)

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | Vocabulary blacklist (`magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful`) — case-insensitive, word-boundary, prose-only | **PASS** | 0 hits in prose. Also scanned inside code blocks (incl. comments) per the dispatch's "hidden in a code comment" question: **0 hits** there too. |
| 2 | Second person dominant; any third-person passive is intentional and labeled | **PASS** | All prose paragraphs are second-person ("you have", "start with", "compare", "your account", etc.). No third-person passive. |
| 3 | Contractions used naturally; no exclamation marks | **PASS (LOW observation)** | 0 exclamation marks. **LOW:** contraction count in prose = 0. The prose uses "does not", "do not" instead of "doesn't", "don't" — slightly more formal than the style guide's voice ("contractions yes"). Matches the friendly-tutor posture but trended more formal than the guide's example list. Not blocking; flagged as a copy-edit-pass note. |
| 4 | Pacing: one move per paragraph; **every paragraph ≤ 80 words** | **WARN** | 34 visible prose paragraphs total. 33 are ≤ 80 words. **One violation:** `ch-07.md:123` = **85 words** (5 over). Verified by hand-count + script. The dispatch's pre-flagged paragraph is confirmed and is at the exact threshold. Per dispatch: "report as a WARN". The paragraph is dense (4 moves: ch-06 connection, three-role recap, two-provider comparison, synthesis) but each move is short and they read as one combined beat. Not MEDIUM (not more than 5 over). |
| 5 | Subheading style: sentence-fragment, ≤ 7 words, action-y | **PASS** | 13 H2 subheadings, all 4-7 words, all sentence-fragment + action-y. Longest: "Load the key from `.env`, never source" (7), "Match the body to ch-06's three roles" (7), "Retry on 429 and 5xx with backoff" (7), "Keep keys out of source and git" (7), "Check: a deliberately-broken endpoint loops then fails" (7). All under or at the cap. |

### Terminology & citation (line-edit focus)

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 6 | All non-obvious claims have inline named sources | **PASS** | Citations present: Python Software Foundation `urllib.request` (`ch-07.md:7`), requests quickstart + advanced-usage pages (`ch-07.md:62`), python-dotenv 1.2.2 release behavior (`ch-07.md:117`), OpenAI Python SDK reference (`ch-07.md:123, 161, 273`), Anthropic Python SDK reference (`ch-07.md:123, 161`), IETF RFC 6585 §4 (`ch-07.md:215`), RFC 7231 §7.1.3 (`ch-07.md:215, 224`), RFC 5737 (`ch-07.md:359`). All non-obvious claims have an inline source. |
| 7 | SDK attribution cites are at the right call sites (3 required) | **PASS** | `openai/openai-python` cited at `ch-07.md:123, 161, 273` (3 sites). `anthropics/anthropic-sdk-python` cited at `ch-07.md:123, 161` (2 sites). The 3 required call sites from dev-fix1 (`:123` Anthropic + OpenAI, `:161` both, `:273` OpenAI-only) are all present. |
| 8 | `gpt-4o-mini` ONLY as configurable default of `MODEL = os.getenv(...)` + 1 prose note; `claude-3-5-sonnet-latest` absent; no other concrete model in request bodies | **PASS** | `gpt-4o-mini` total prose-only hits: **1** (line 43, the "1 prose note" — mentions the configurable default). All 5 code-block uses are inside `MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")` at `ch-07.md:16, 70, 131, 179, 306`. `claude-3-5-sonnet-latest`: 0 hits. No concrete model identifier in any request body — the TEST-NET-1 demo at `ch-07.md:376` correctly uses `"x"` as the placeholder. |
| 9 | Acronyms expanded on first use: HTTP, API, SDK, JSON (LLM if used) | **WARN (copy-edit-pass material)** | **None** of HTTP, API, SDK, JSON are expanded on first prose use. First prose occurrences: HTTP at `ch-07.md:7`, API at `ch-07.md:3`, JSON at `ch-07.md:3`, SDK at `ch-07.md:123`. LLM is not used in ch-07 prose (so no re-expansion needed; ch-06's expansion carries forward). The expansions **do** live in `bible.md:97-100` ("HTTP (Hypertext Transfer Protocol)", "API (Application Programming Interface)", "JSON (JavaScript Object Notation)", "SDK (Software Development Kit)"). Per the ch-06 ledger pattern ("IBM + API acronym expansions at ch-06.md:7, :29 — both copy-edit-pass material"), this is **copy-edit-pass material**, not a line-edit blocker. Flagging as WARN. |

### Structure & alignment

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 10 | Orientation paragraph: 30–60 words | **PASS** | `ch-07.md:3` = **48 words**. Inside the band. |
| 11 | Forward-pointer "What's next" names ch-08 with concrete forward move (30-line plain-Python agent loop) | **PASS** | `ch-07.md:412` reads: "What's next: ch-08 builds a thirty-line plain-Python agent loop that prompts the model, parses a single action from the reply, runs one tool, feeds the result back, and loops until the model emits "done" — the toy agent that ch-09's framework introduction lands on." Names ch-08 explicitly; concrete move named (thirty-line plain-Python agent loop; prompt → parse → tool → feedback → done). **LOW observation:** the bridge is 44 words — slightly long for "thin", but contains all required content. Not blocking. |
| 12 | Closing imperative (`> **The move:**`) is the FINAL visible substantive prose paragraph before the HTML comment; thin "What's next" bridge permitted between | **PASS** | Order: `ch-07.md:410` outcome-imperative (blockquote) → `ch-07.md:412` "What's next" bridge (44 words) → `ch-07.md:414` HTML comment. Matches the dispatch's permitted order. |
| 13 | Zero handoff-style recap, zero authorial summary, zero third-person "by the end of the reading…" closing line | **PASS** | No handoff-style recap after the imperative. No "in this chapter we explored…" sentence. No third-person close. The chapter ends imperative → bridge → HTML comment. |

### No-regression vs dev-fix1

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 14 | Word count 1722 (±10% = 1548–1894) | **PASS** | This reviewer's count: 1597. Inside 1548-1894 band. The writer's count (1722) is also inside the band. No regression — the post-fix1 chapter is within tolerance. (Methodology noise accounts for the 125-word delta; both numbers are admissible.) |
| 15 | UTF-8 clean round-trip | **PASS** | Round-trip clean. 69 non-ASCII bytes (em dash, curly quotes). No encoding artifacts. |
| 16 | No HfApiModel / ApiModel mention (whole-book rule) | **PASS** | 0 hits for `HfApiModel`. 0 hits for `ApiModel`. The only `HfApiModel` token in the entire book is reserved for the ch-09 sidebar. |
| 17 | bible.md earlier chapter blocks (ch-01..ch-06) untouched | **PASS** | bible.md ch-06 block ends at line 94; ch-07 block appended at lines 95-112 with the ch-07 glossary entries. ch-01..ch-06 blocks preserved verbatim. |
| 18 | ledger.md ch-07 row updated correctly | **PASS** | ledger.md:145 ch-07 row lists all 8 dev-fix1 fixes, status `drafted`, dev-review column `dev-fix1`, line-edit column `-`, word count 1722, full fix-loop narrative. No errors. |

---

## Cross-cutting findings

1. **The `ch-07.md:123` 85-word paragraph is the one-and-only structural violation in the chapter.** All 33 other visible prose paragraphs are ≤ 80 words (closest runner-up: `ch-07.md:43` 75 words, `ch-07.md:211` 67 words, `ch-07.md:119` 65 words, `ch-07.md:277` 64 words). The chapter is pacing-consistent except for this one beat. The writer's self-flag was accurate.

2. **Acronym expansion pattern matches the ch-06 ledger convention.** ch-06 had a similar line-edit finding ("IBM + API acronym expansions at ch-06.md:7, :29 — both copy-edit-pass material") and ch-07 follows the same pattern. The bible carries the canonical expansions; the chapter prose uses the bare acronyms. Treat the whole-book copy-edit pass as the right venue to land inline acronym expansions in one coordinated pass across all chapters.

3. **No subtle technical issues in the credential helper, retry loop, or `Retry-After` parser that the dev-fix1 review missed.** Verified by hand:
   - `load_api_key(name)` (`ch-07.md:104-109`): `load_dotenv()` inside the helper, `os.getenv(name)` with explicit `if not api_key: raise SystemExit(...)`. Returns the key. The `# reads ./.env, walks upward, sets os.environ` comment is accurate (python-dotenv's `find_dotenv()` walks up). Re-call of `load_dotenv()` on every helper invocation is harmless.
   - Retry loop (`ch-07.md:182-208`): handles `requests.exceptions.HTTPError` with code check (retries 429 and 5xx, re-raises 4xx); handles `ConnectionError` + `Timeout` separately with the same backoff; `(2 ** attempt) + random.uniform(0, 0.5)` backoff is correct; final `raise RuntimeError(...)` on exhaustion. No race, no off-by-one, no leak.
   - `parse_retry_after()` (`ch-07.md:223-238`): tries integer-seconds form first (`float(int(value))`); on `ValueError`, falls through to `parsedate_to_datetime()` for HTTP-date form; on `None` or `(TypeError, ValueError)`, falls back to `2 ** attempt`. Caps both at `min(60.0, max(0.0, …))` so the result is always `[0, 60]`. Timezone-naive parsed-date edge case is handled (Python 3.6+ `parsedate_to_datetime` returns aware datetimes; the `try/except (TypeError, ValueError)` covers any legacy path). No bugs.

4. **Code-block blacklist re-scan (per the dispatch's "hidden in a code comment" question): 0 hits.** The dev-fix1 review was thorough; no `magic` / `just` / `simply` / `optimal` / `powerful` slipped into a `# comment` or a docstring.

5. **TEST-NET-1 demo (`ch-07.md:357-408`) is the only chapter runnable check.** The post-fix1 `b'{"model":"x","messages":[]}'` payload (line 376) is intentionally a placeholder — the demo is supposed to hit the network-error branch, not parse a model name. Verified by dev-fix1 per ledger. The cross-platform guarantee (Windows / macOS / Linux all treat `192.0.2.1` as unrouted) is documented in prose at line 359 with the RFC 5737 citation.

---

## Out-of-scope observations (non-blocking)

- **`ch-07.md:412` "What's next" bridge is 44 words** — slightly long for a "thin bridge", but the dispatch's "thin" qualifier is informal and the bridge content (ch-08 + 30-line plain-Python agent loop + prompt→parse→tool→feedback→done) is exactly what the chapter needs to hand off. Not blocking.
- **Zero contractions in prose** — the voice is slightly more formal than the style guide's "contractions yes" rule. A copy-edit pass can sprinkle in `don't`, `won't`, `it's` if the whole-book voice wants more contraction density. Not blocking for ch-07 alone; the consistency choice is a whole-book decision.
- **`ch-07.md:43` "Each example below defines a `MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")` constant" is 75 words** — under the cap, but it does pack two moves (re-state the model-id rule + pivot to the `requests` package). Borderline. Not blocking.
- **`ch-07.md:123` 85-word paragraph has 4 distinct moves in 4 sentences** (ch-06 connection, three-role recap, two-provider comparison, synthesis). The "one move per paragraph" rule from the style guide is technically stretched. The sentences are short and read as one combined beat, so the practical rhythm is preserved. The 5-word overshoot is the visible symptom; the underlying density is the real story. Per the dispatch's "5 over = WARN" guidance, this is WARN, not MEDIUM.

---

## Honest assessment

**Did I count the words at ch-07.md:123?** Yes — by hand (tokenized on whitespace) and by script. Both methodologies agree: **85 words**. The writer's self-flag was correct and accurate. The paragraph is exactly 5 over the 80-word cap, at the threshold the dispatch specified for a WARN (not MEDIUM).

**Any other paragraph-length violations?** No. I counted every visible prose paragraph (34 total) and only `ch-07.md:123` is over 80 words. The next-longest is `ch-07.md:43` at 75 words. The chapter is pacing-consistent except for this one beat.

**Any subtle issues with the credential helper, retry loop, or `Retry-After` parsing that the dev-fix1 review missed?** No. I audited all three by hand. They are correct, complete, and idiomatic. The credential helper has one minor cosmetic note (calling `load_dotenv()` on every helper invocation is harmless but slightly redundant) — not a bug. The retry loop handles all four buckets correctly. The `Retry-After` parser handles both RFC 7231 forms with a 60s cap and a sane default fallback.

**Any blacklist word hidden in a code comment or inline citation that the dev reviewer didn't scan?** No. I ran the full blacklist scan (10 terms) over the code blocks including comments, and the result is 0 hits. The dev-fix1 review was thorough.

**One thing the writer should know for the copy-edit pass:** the orientation paragraph at `ch-07.md:3` is 48 words (in band) and is the one place where a single in-prose parenthetical like "HTTP (Hypertext Transfer Protocol)" or "API (Application Programming Interface)" would land naturally without breaking flow. The bible carries the canonical expansions; the whole-book copy-edit pass is the right time to make this consistent across all chapters. ch-07 is not uniquely out of compliance — it follows the same convention as ch-06 and the rest of the book so far.

**Verdict rationale:** the chapter is structurally clean, technically sound, voice-consistent, citation-complete, and pacing-acceptable except for one 5-word overshoot at `ch-07.md:123`. The acronym-expansion note is a whole-book copy-edit concern, not a ch-07-specific failure. The line-edit verdict is **PASS_WITH_WARN**.

---

## Self-critique

What this review could miss:
- **Subtle cross-chapter references.** I confirmed the ch-08 forward pointer names ch-08 and the 30-line plain-Python agent loop, but I did not verify that the ch-08 chapter outline actually delivers the 30-line plain-Python agent loop. If ch-08 diverges, the forward pointer becomes a contract violation. This is a planning/master concern, not a ch-07 line-edit concern. (The ch-08 outline row in ledger.md:157 says "Plain Python only (no smolagents, no `@tool`, no `CodeAgent`)" — consistent with the ch-07 forward pointer.)
- **Style guide updates since the writer started.** The style guide I audited is dated DRAFT. If the user has since approved an updated style guide that differs from the DRAFT version I read, the verdict could change. Low risk — the DRAFT guide is internally consistent and the writer followed it.
- **Word-count methodology.** My count (1597) differs from the writer's (1722) by 125 words. I did not reverse-engineer the writer's exact methodology to within a few words; I verified the chapter is in the dispatch's 1548-1894 band, which both numbers satisfy. If the user's whole-book word-count tracker uses a different methodology, the per-chapter counts would all need a single re-pass. Not blocking.
- **I did not run the chapter's runnable check.** I did not re-execute the TEST-NET-1 demo. The ledger says the dev-fix1 review verified it (line 145 of ledger.md: "TEST-NET-1 demo re-verified clean after edits"). A line-edit review by spec does not re-run code; dev review is the verification layer. If a re-run is desired, it is a dev review concern, not line-edit.

---

## Recommended next action

- **For the writer:** the only line-edit fix the chapter needs is a 5-word trim at `ch-07.md:123` to bring it from 85 → ≤ 80 words. (Possible trim: cut the four-word synthesis tail "The shape that survives both providers is the list of message dicts." and let the two-provider comparison stand on its own — saves 14 words and lands the paragraph at 71. Or fold the synthesis into the next paragraph.) This is a 1-paragraph, 5-10 minute fix.
- **For the copy-edit pass:** the four acronym expansions (HTTP, API, JSON, SDK) belong to a whole-book pass, not ch-07 alone.
- **For master:** after the writer trims `ch-07.md:123`, this chapter moves from `drafted` → `line-edited`. No other blockers.

**Overall verdict: PASS_WITH_WARN** — ready for the writer to land the 5-word trim at `ch-07.md:123`; everything else is whole-book copy-edit material.
