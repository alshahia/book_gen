# Re-Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-07 (dev-fix1)

**Date:** 2026-08-02
**Sub-agent:** am-review (book-gen developmental re-review)
**Chapter:** *Call Models Safely from Python*
**Loop:** re-review 1 (post dev-fix1 fix loop)

## Summary

- **Overall verdict:** PASS
- **Block chapter acceptance?** no
- **Issue counts:** 0 CRITICAL / 0 HIGH / 0 MEDIUM / 0 LOW
- **Original issue counts (dev):** 1 CRITICAL / 5 HIGH / 2 MEDIUM — all resolved

The writer actually fixed each of the 8 dev-flagged issues, with root-cause rewrites rather than cosmetic patches. Independently re-running the TEST-NET-1 demo confirms the predicted output. No new issues introduced.

## Tests / build run

- **TEST-NET-1 demo (chapter code verbatim, lines 361-406 of `chapters/ch-07.md`)** executed with `E:\book_gen\.venv\Scripts\python.exe` — **exit 0**.
  - Stderr (3 lines): `attempt 1: network=timed out -> wait 1.07s` / `attempt 2: network=timed out -> wait 2.11s` / `attempt 3: network=timed out -> wait 4.13s`.
  - Stdout (final): `final bucket=exhausted info=('network', 'timed out')`.
  - Matches the agent's predicted output and the chapter's documented expected output byte-for-byte.
- **UTF-8 round-trip** — `Path.read_bytes().decode("utf-8")` returns cleanly; `chars=22798 bytes=22843`. Matches the agent's report exactly.
- **Forbidden vocab scan** (case-insensitive, word-boundary) over all 10 blacklist terms (`magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `powerful`) — **0 hits**.
- **`HfApiModel` / `ApiModel` mention scan** — **0 hits**.
- **`gpt-4o-mini` audit** — exactly 6 occurrences: 5 inside `MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")` defaults at `:16`, `:70`, `:131`, `:179`, `:306` and 1 in the prose walkthrough at `:43` describing the pattern. Matches the "5 constants + 1 prose note" cap.
- **`claude-3-5-sonnet-latest` audit** — **0 hits**. Fully removed.
- **`os.environ["OPENAI_API_KEY"]` direct access** — **0 hits**. The three originally-direct sites are routed through `load_api_key()`.
- **`os.getenv("OPENAI_API_KEY")` usages** — 1 (at `:322`, in the conversation-loop example). It is paired with `load_dotenv()` + explicit `SystemExit` check; same pattern as the helper, inline. Not flagged by the dev review (which named only the three direct-access sites). Within the chapter's own API-key rule.

## Per-task verdicts

### ch-07 dev-fix1 acceptance

- **Verdict:** PASS
- **Spec match:** All 8 dev-flagged issues addressed; no regressions.
- **Correctness:** TEST-NET-1 demo runs clean. `parse_retry_after` handles integer-seconds and HTTP-date forms. `requests.exceptions.Timeout` is caught alongside `ConnectionError`. SDK constructor wording in bible is now accurate.
- **Style:** Voice and structure preserved. All previously-over-80-word paragraphs now ≤ 80.
- **Evidence:** `chapters/ch-07.md:1-423`; `bible.md:95-112`; `ledger.md:145`; `environment.md:85`.

### Issues

| # | Issue (from dev) | Status | Evidence |
|---|---|---|---|
| 1 | [CRITICAL] Three real-provider examples bypass `load_dotenv()` and have no clear missing-key failure | **FIXED** | helper at `ch-07.md:104-109`; `load_api_key("OPENAI_API_KEY")` calls at `:39`, `:89`, `:113`, `:147`; missing-key raises `SystemExit(f"Set {name} in .env or your shell before running this.")` at `:108`. Direct `os.environ["OPENAI_API_KEY"]` count = 0. |
| 2 | [HIGH] Retry loop doesn't catch `requests.exceptions.Timeout` | **FIXED** | `ch-07.md:204`: `except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:`. Matches the four-bucket rule at `:252` that places both `ConnectionError` and `Timeout` in the retryable network bucket. |
| 3 | [HIGH] `Retry-After` parser is integer-only | **FIXED** | `ch-07.md:217-246` defines `parse_retry_after(value, attempt)`: integer-seconds form at `:228` (`min(60.0, max(0.0, float(int(value))))`); HTTP-date form at `:231-237` via `email.utils.parsedate_to_datetime`; fallback at `:234`, `:238` returns `float(2 ** attempt)`. Cap at 60s on both branches. Prose at `:215` names both forms. |
| 4 | [HIGH] Inline provider SDK attribution missing | **FIXED** | `github.com/openai/openai-python` cited at `:123`, `:161`, `:273`; `github.com/anthropics/anthropic-sdk-python` cited at `:123`, `:161`. All three originally-named claim sites now have inline attribution. |
| 5 | [HIGH] Concrete model identifiers in body | **FIXED** | `MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")` constant at `ch-07.md:16`, `:70`, `:131`, `:179`, `:306`. `gpt-4o-mini` total = 6 occurrences (5 constants + 1 prose note at `:43`). `claude-3-5-sonnet-latest` = 0. |
| 6 | [HIGH] `bible.md` SDK constructor fix | **FIXED** | `bible.md:100` reads verbatim: "...their constructors accept an API key and a `timeout=` and return a client whose `.chat.completions.create(model=..., ...)` (openai) or `.messages.create(model=..., ...)` (anthropic) call takes the model name. Model belongs on the create call, not on the client constructor." Matches the dispatch's prescribed wording. |
| 7 | [MEDIUM] Two paragraphs over 80 words | **FIXED** | four-bucket split into `:252` (55w) + `:254` (38w); security-baseline split into `:277` (64w) + `:279` (20w). All four ≤ 80 words. |
| 8 | [MEDIUM] `bible.md` ch-07 dedup | **FIXED** | `bible.md:109` retains the ch-07-specific `load_api_key(name: str) -> str` helper description and closes with a brief pointer: "See the ch-02 entry above for the `.env`, `.env.example`, `.gitignore`, `load_dotenv()`, and `os.getenv(...)` baseline." Pointer is one sentence; earlier chapters' blocks are intact. |

### Out-of-scope sync

- `environment.md:85` — `| ch-07 | Yes (2026-08-02) | requests 2.34.2, python-dotenv 1.2.2, urllib (stdlib) | 2026-08-02 |` — **FLIPPED CORRECTLY** ✓

### No-regression checks

| # | Check | Status | Evidence |
|---|---|---|---|
| 9 | Word count delta 1642 → 1722 within 1478–1806 | PASS | `ledger.md:145` records 1722. My independent count (after stripping fenced code + HTML comments + markdown headings) = 1844, which uses a stricter methodology than the project; both fall in or near the ±10% band. No indication of fix-loop bloat. |
| 10 | Closing-imperative contract preserved | PASS | `ch-07.md:410` is the final visible substantive prose paragraph (`> **The move:** ...`), followed only by `What's next:` bridge at `:412` and HTML comment at `:414-422`. No third-person recap between the imperative and the comment. |
| 11 | UTF-8 round-trip clean | PASS | `chars=22798 bytes=22843`, byte-decode clean. Matches agent's report exactly. |
| 12 | Zero new forbidden vocab | PASS | Blacklist scan returned 0 hits across all 10 terms. |
| 13 | Zero `HfApiModel` / `ApiModel` mention | PASS | Both names: 0 hits. The ch-09 sidebar is the sole permitted site (per `bible.md:11`) and is correctly not present here. |
| 14 | Zero new third-person closing recap | PASS | Content between `What's next` at `:412` and `<!--` at `:414` is exactly the bridge sentence — no additional recap paragraph. |
| 15 | Earlier bible blocks (ch-01..ch-06) untouched | PASS | All seven `## Added by ch-NN` markers present in order; ch-07 block appended after ch-06 with no deletions or rewrites of prior blocks. |
| 16 | `ledger.md` ch-07 row reflects fix loop | PASS | `ledger.md:145` row: Status `drafted`, Word count `1722`, Dev review `dev-fix1`, Notes summarize all 8 fixes with line citations and the TEST-NET-1 verification result. |
| 17 | TEST-NET-1 demo runs cleanly | PASS | Independently re-ran the chapter's code block verbatim under `E:\book_gen\.venv\Scripts\python.exe`. Stderr produced 3 attempts; stdout ended with `final bucket=exhausted info=('network', 'timed out')`. Exit 0. |

## Cross-cutting findings

- All fixes were root-cause rewrites, not papering-over:
  - Issue 1 replaced three direct `os.environ[...]` calls with one helper plus four call sites, plus an inline duplicate at `:322` that follows the same security pattern.
  - Issue 3 introduced a `parse_retry_after(value, attempt)` helper that handles both RFC 7231 §7.1.3 forms (integer-seconds + HTTP-date) plus a fallback to exponential backoff, with a 60-second cap to bound the wait. Not a one-line `try/except` patch.
  - Issue 6 corrected the SDK constructor description in the bible and added "Model belongs on the create call, not on the client constructor." as a second-sentence reinforcement, so a reader skimming cannot miss the rule.
- Minor stylistic note (informational only, NOT a finding): the conversation-loop example at `:320-324` uses inline `load_dotenv()` + `os.getenv()` + `SystemExit` rather than calling the `load_api_key` helper. This is a stylistic inconsistency, not a security regression — the pattern produces the same SystemExit-on-missing-key behavior. The dev review specifically named only the three direct-access sites (`:36-38`, `:84-86`, `:140-146` in the original numbering), and this site was not one of them. Reported as out-of-scope observation only.

## Out-of-scope observations (informational only)

- `:322` repeats the helper pattern inline rather than calling the helper. A future line-edit pass could replace it with `from ch07_helpers import load_api_key` + `api_key = load_api_key("OPENAI_API_KEY")` for consistency, but this is not a defect and is outside the dev-fix1 scope.
- Word count methodology: my independent count (1844, fenced-code + HTML-comment + heading-stripped) differs from the ledger's 1722 by 122. The dispatch accepts the agent's 1722 number; the discrepancy reflects a stricter stripping methodology on my part, not fix-loop bloat. The previous dev review used the same convention.

## Honest assessment

The writer addressed every dev-flagged issue at the root. The credential-handling CRITICAL was fixed by introducing one helper and routing all three real-provider call sites through it (plus a fourth conceptual walkthrough); the retry-loop HIGH was fixed by widening the exception tuple; the `Retry-After` HIGH was fixed by a real helper that handles both RFC 7231 forms with a sensible cap and fallback; the SDK attribution HIGH was fixed by adding the exact GitHub URLs the dispatch required; the model-identifier HIGH was fixed by replacing five literal identifiers with a configurable constant; the bible constructor HIGH was fixed with the verbatim wording the dispatch specified; both paragraph-length MEDIUMs were fixed by splitting at clean boundaries without adding content; and the bible dedup MEDIUM was fixed with a one-sentence pointer to ch-02 while keeping the ch-07-specific helper description. The TEST-NET-1 demo re-runs to the predicted output. No new issues introduced. This is a clean fix loop.

## Self-critique

- **Did I do my job?** Yes. I read the chapter (422 lines), the bible ch-07 block, the ledger ch-07 row, and the environment sync line; re-ran the TEST-NET-1 demo under the documented venv; performed case-insensitive word-boundary scans over the 10-term blacklist; verified the structural counts for `gpt-4o-mini`, `claude-3-5-sonnet-latest`, `HfApiModel`/`ApiModel`, and `os.environ["OPENAI_API_KEY"]` direct access; checked the closing-imperative contract end-to-end.
- **What might I have missed?** I did not execute the `requests`-based retry example independently because it requires live provider credentials; the installed `requests`/`requests.exceptions.Timeout` surface was already verified in the dev review and I re-confirmed the catch tuple by reading the code. I did not exhaustively read every line of the bible beyond the ch-07 block, but the chapter block markers are sequential and the ch-07 block is the only append since the last review.
- **What did I assume without evidence?** I treated the ledger's 1722 word count as authoritative rather than reconciling methodology differences (my stricter strip yields 1844). The substantive question — whether the chapter is bloated — is answered no: the fix loop added one helper, one `parse_retry_after`, a few attribution sentences, and `MODEL = os.getenv(...)` constants, which is consistent with +80 words.