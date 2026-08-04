# Book Dev Fix-Loop Re-review — T-2026-08-01-001-book-ai-agents-with-python / ch-17 / dev-fix1

**Date:** 2026-08-03
**Sub-agent:** am-review (book-gen mode)
**Loop:** dev fix loop 1
**Chapter:** ch-17 — Choose and Operate Model Backends

## Summary

- **Overall verdict:** PASS
- **Scope reviewed:** 2 surgical fixes plus 6 no-regression checks
- **Issue counts:** CRITICAL 0 / HIGH 0 / MEDIUM 0 / LOW 0
- **Block progression to line edit?** no

Both requested fixes are real and complete. The closing callout is now a direct second-person imperative, and the first prose use of CUDA is expanded naturally. Fresh execution of all three Python blocks passed, and the specified chapter/bible/ledger invariants hold.

## Tests / build run

- `E:\book_gen\.venv\Scripts\python.exe <combined three extracted Python blocks>` — exit code 0.
  - Inventory block printed `14` and all fourteen names.
  - Environment/model-name block printed `OpenAIModel`, `InferenceClientModel`, and both small defaults.
  - Factory block printed `openai: OpenAIModel`, `anthropic: LiteLLMModel`, `hf: InferenceClientModel`, and `local: TransformersModel`.
- Python AST parsing was performed before execution for all 3 extracted blocks — 3/3 passed.
- UTF-8 byte decode/encode round-trip — clean; zero replacement characters.
- Chapter regex checks — `\bby the end of the reading\b` = 0; `\bthe reader\b` = 0; `\byou\b` = 8; `\bHfApiModel\b` = 0.
- Dispatch-authoritative word-count delta — 1601 → 1600 (−1), within the required 1441–1761 band. An independent simplified prose counter produced 1457 because its tokenization strips inline-code content; this does not contradict the ledger/workflow count supplied for the fix loop.

## Per-task verdicts

### Fix 1 — Closing imperative

- **Verdict:** PASS
- **Spec match:** The callout uses the exact dispatched rewrite and begins with direct commands: “Build,” “instantiate,” “pass,” “confirm,” and “add.”
- **Correctness:** It addresses the reader in second person (`your`, `you`) and contains neither banned third-person phrase.
- **Evidence:** `books/ai-agents-with-python/chapters/ch-17.md:159`; fresh regex counts listed above.
- **Issues:** none.
- **Suggested fix:** no fix needed.

### Fix 2 — CUDA acronym expansion

- **Verdict:** PASS
- **Spec match:** The first prose mention now reads “CUDA (NVIDIA's Compute Unified Device Architecture for GPU computing).”
- **Correctness:** The expansion appears at the required line and reads naturally in the sentence about GPU support for vLLM.
- **Evidence:** `books/ai-agents-with-python/chapters/ch-17.md:85`.
- **Issues:** none.
- **Suggested fix:** no fix needed.

### No-regression checks

- **Verdict:** PASS
- **Word count:** `books/ai-agents-with-python/ledger.md:265` records 1600 and the fix-loop note records 1601→1600.
- **UTF-8:** `books/ai-agents-with-python/chapters/ch-17.md:1-165` round-trips cleanly.
- **Executable code:** all 3 blocks at `books/ai-agents-with-python/chapters/ch-17.md:15-39`, `:49-63`, and `:101-130` parse and run cleanly with the required venv interpreter.
- **Whole-book rename rule:** chapter contains zero `HfApiModel` mentions; the only historical mention remains in the ch-09 bible block at `books/ai-agents-with-python/bible.md:96`.
- **Bible invariant:** `books/ai-agents-with-python/bible.md:1-189` remains 189 lines with ch-01 through ch-16 blocks intact and no ch-17 block.
- **Ledger invariant:** `books/ai-agents-with-python/ledger.md:265` alone carries the ch-17 `dev-fix1`, 1600-word fix-loop update; the visible ch-01 through ch-16 rows remain intact at `ledger.md:73-253`. This workspace is not a Git repository, so row-level VCS diff proof was unavailable; verification used the supplied pre-fix report plus direct inspection.
- **Issues:** none.
- **Suggested fix:** no fix needed.

## Cross-cutting findings

- The closing rewrite preserves the required operational sequence: choose through a factory, instantiate with `model_id`, pass the model to `CodeAgent`, test class-name selection offline, and use `OpenAIServerModel(api_base=...)` for compatible hosted/self-hosted endpoints (`ch-17.md:159`).
- The broader chapter still retains the fourteen-name surface (`ch-17.md:18-41`), the Anthropic path through `LiteLLMModel(model_id="anthropic/...")` (`ch-17.md:69`, `:141`), the factory map (`ch-17.md:101-130`), and the three-member `*ServerModel` family (`ch-17.md:41`, `:75-79`).

## Out-of-scope observations

- None.

## Honest assessment

The writer actually fixed both findings rather than hiding them: the banned closing was replaced with imperative instructions, and CUDA received a genuine first-use expansion. No new issue was introduced by either edit. The shorter closing no longer enumerates all fourteen names or spells out the Anthropic adapter inline, but it preserves those substantive elements through the unchanged inventory, provider-selection prose, runnable mapping, and server-family discussion; the closing itself still preserves the factory and `OpenAIServerModel` action path.

## Self-critique

- **Did I do my job?** Yes. I read the prior FAIL report and current chapter, bible, and ledger; verified both changed lines; ran all three code blocks fresh; and checked every requested regex and file invariant.
- **What might I have missed?** A byte-for-byte comparison of every non-ch-17 ledger row against a pre-fix filesystem snapshot was impossible because the workspace is not a Git repository and no separate snapshot was provided.
- **What did I assume without evidence?** I accepted the workflow's stated 1601→1600 word-count methodology because the independent simplified counter treats inline code differently; the authoritative ledger row and dispatched delta agree.
