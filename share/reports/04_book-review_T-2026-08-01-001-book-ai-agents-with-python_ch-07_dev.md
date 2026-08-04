# Developmental Review — T-2026-08-01-001-book-ai-agents-with-python / ch-07

**Date:** 2026-08-02
**Sub-agent:** am-review (book-gen developmental pass)
**Chapter:** *Call Models Safely from Python*

## Summary

- **Overall verdict:** FAIL
- **Block chapter acceptance?** yes
- **Issue counts:** 1 CRITICAL / 5 HIGH / 2 MEDIUM / 0 LOW
- **Word count:** 1,642 — within the supplied 1,080–1,760 band and its ±10% tolerance

The chapter has the right instructional spine and covers all ten research entries, but it does not yet satisfy its own API-key security baseline, timeout taxonomy, source-grounding rule, or binding age-risk style rule. The TEST-NET-1 check and installed SDK surfaces were independently verified.

## Tests / build run

- `E:\book_gen\.venv\Scripts\python.exe` signature inspection for `requests`, `dotenv`, `openai`, and `anthropic` — **exit 0**.
  - `requests.post(url, data=None, json=None, **kwargs)` accepts `json=` and forwarded `timeout=`.
  - `requests.Response.raise_for_status()` and `requests.Response.json(**kwargs)` exist.
  - `load_dotenv(dotenv_path=None, stream=None, verbose=False, override=False, interpolate=True, encoding="utf-8")` matches the chapter's use.
  - `openai.OpenAI(..., timeout=..., max_retries=...)` and `client.chat.completions.create(messages=..., model=..., timeout=...)` exist in `openai==2.52.0`.
  - `anthropic.Anthropic(..., timeout=..., max_retries=...)` and `client.messages.create(max_tokens=..., messages=..., model=..., system=..., timeout=...)` exist in `anthropic==0.120.2`.
  - Both installed clients expose `with_options` — **exit 0**.
- Exact TEST-NET-1 Python block extracted from `chapters/ch-07.md` and executed with `E:\book_gen\.venv\Scripts\python.exe` — **exit 0**. Final stdout: `final bucket=exhausted info=('network', 'timed out')`; stderr contained three network attempts with backoff.
- UTF-8 byte decode using `Path.read_bytes().decode("utf-8")` — **exit 0**, `utf8_ok 20785 20744`.
- Automated structural scan — 13 H2 headings; every H2 is 4–7 words; zero blacklist hits in manuscript prose; no `HfApiModel` or `ApiModel` occurrence; no literal outcome-style third-person closing.

## Required checklist

1. **Outline coverage — PASS.** All ten entries are substantively present: entry-051 at `chapters/ch-07.md:5-56`; entry-052 at `:58-89`; entry-053 at `:91-115`; entry-054 at `:117-149`; entry-055 at `:151-161`; entry-056 at `:163-203`; entry-057 at `:205-217`; entry-058 at `:219-240`; entry-059 at `:242-258`; entry-060 at `:260-307`.
2. **Voice match — PASS.** The opening addresses the reader directly (`chapters/ch-07.md:3`), contractions occur naturally (`:155`, `:203`), and there are no prose exclamation marks. The `!` character found by a raw scan is the `!=` operator at `:191`, not punctuation.
3. **Vocabulary blacklist — PASS.** Case-insensitive word-boundary scan found zero occurrences of all ten forbidden terms in the visible manuscript.
4. **Bible consistency — FAIL.** The required ch-07 block exists at `bible.md:95-111` and includes the required concepts, but it repeats the already-established `.env` / `load_dotenv()` material from `bible.md:49-51` rather than remaining cleanly non-duplicative. It also says provider SDK constructors accept a model name at `bible.md:100`; installed `OpenAI` and `Anthropic` constructors do not—the model is supplied to `chat.completions.create(...)` or `messages.create(...)`.
5. **Research grounding — FAIL.** The chapter names the Python Software Foundation at `chapters/ch-07.md:7`, requests documentation at `:60`, and RFC 6585 at `:207`, but provider claims at `:119`, `:155`, and `:240` are not attributed inline to the named OpenAI SDK docs and Anthropic SDK docs as required.
6. **Cross-platform correctness — N/A.** This chapter contains no `.venv` activation instructions to validate. Its Python blocks use no OS-specific paths. The TEST-NET check ran on Windows, but the prose's macOS/Linux behavior remains a documentation-based assertion (`chapters/ch-07.md:323`).
7. **Code-block correctness — FAIL.** The installed `requests`, `python-dotenv`, OpenAI, and Anthropic surfaces match the API forms claimed, and the TEST-NET block behaves as predicted. However, the retry implementation catches `ConnectionError` but not `requests.exceptions.Timeout` (`chapters/ch-07.md:196-200`), contradicting the four-bucket rule that both are retryable (`:221`). The `Retry-After` example also assumes an integer delta (`:210-213`), although the header may be an HTTP date; that form raises `ValueError`.
8. **Beginner accessibility — FAIL.** The 48-word orientation meets the 30–60-word rule (`chapters/ch-07.md:3`), and all 13 H2s are action-oriented fragments of at most seven words. Two visible prose paragraphs exceed 80 words: the four-bucket paragraph is about 90 words (`:221`) and the security-baseline paragraph about 82 (`:244`).
9. **Closing-imperative contract — PASS.** `> **The move:**` is the final substantive instructional paragraph (`chapters/ch-07.md:374`), followed only by the permitted thin “What's next” bridge (`:376`) and the HTML comment (`:378`). There is no third-person outcome recap after it.
10. **Forward-pointer hygiene — PASS.** The bridge explicitly names ch-08 and its concrete prompt → parse → tool → feedback → `done` loop (`chapters/ch-07.md:376`).
11. **API-key rule — FAIL.** Three real-provider examples read `OPENAI_API_KEY` directly through `os.environ[...]` without first calling `load_dotenv()` and without the required clear missing-key failure: `chapters/ch-07.md:36-38`, `:84-86`, and `:140-146`. This directly contradicts the chapter's own three-rule baseline at `:242-258`. The example at `:109-110` also prints key length; it does not expose the key, but it teaches unnecessary secret-derived logging.
12. **No HfApiModel / ApiModel mention — PASS.** Zero occurrences in the chapter body.
13. **UTF-8 clean — PASS.** Fresh byte decode completed with zero errors.
14. **No-regression vs prior chapters — PASS.** The ledger's ch-07 row is present, remains `drafted`, records dependency on ch-06 and word count 1,642 (`ledger.md:145`). The bible adds the ch-07 block after ch-06 without deleting or rewriting prior blocks (`bible.md:82-111`). The duplication and constructor wording are separately captured under checklist item 4.

## Per-task verdict

### ch-07 developmental acceptance

- **Verdict:** FAIL
- **Spec match:** The chapter covers the intended material and closes on the supplied outcome, but the examples do not uniformly enforce the outcome's `.env` and missing-key contract.
- **Correctness:** Installed APIs and the TEST-NET demonstration check out; timeout retry handling and `Retry-After` parsing are incomplete.
- **Style:** Voice and headings match, while two paragraph-length violations and repeated exact provider model identifiers break binding style rules.
- **Evidence:** `chapters/ch-07.md:3-376`; `style-guide.md:139-153`; `bible.md:95-111`; `ledger.md:145`.

## Issues

- **[CRITICAL]** `chapters/ch-07.md:36-38`, `:84-86`, and `:140-146` show real-provider calls that bypass `load_dotenv()` and do not fail fast with the chapter's clear missing-key message. A reader following these examples gets a raw `KeyError` and the chapter violates checklist item 11 plus its own baseline at `:242-258`. **Fix:** route every real-key example through the demonstrated `load_api_key()` helper or inline the same `load_dotenv()` + `os.getenv()` + `SystemExit` check.
- **[HIGH]** `chapters/ch-07.md:196-200` does not catch `requests.exceptions.Timeout`, while `:221` explicitly places timeout in the retryable network bucket. **Fix:** catch `(requests.exceptions.ConnectionError, requests.exceptions.Timeout)` in the retry loop and in the final network mapping as appropriate.
- **[HIGH]** `chapters/ch-07.md:210-213` parses every `Retry-After` value with `int(...)`; HTTP permits either delay-seconds or an HTTP date. **Fix:** handle both forms or explicitly state and safely fall back when the value is not an integer.
- **[HIGH]** API-surface claims at `chapters/ch-07.md:119`, `:155`, and `:240` lack inline attribution to the named OpenAI SDK docs and Anthropic SDK docs required by the dispatch. **Fix:** name each provider's official SDK reference at the claim site rather than using “the SDK reference page.”
- **[HIGH]** The binding age-risk table forbids concrete provider model identifiers (`style-guide.md:139-153`), yet `gpt-4o-mini` appears repeatedly in code at `chapters/ch-07.md:17`, `:74`, `:132`, `:176`, and `:276`. **Fix:** use a directional placeholder/config variable and tell the reader to choose a currently supported small provider model.
- **[HIGH]** `bible.md:100` inaccurately says the OpenAI and Anthropic SDK constructors accept a model name; fresh installed-signature inspection shows model belongs on the create call. **Fix:** correct the ch-07 append without rewriting earlier chapter blocks.
- **[MEDIUM]** Visible prose paragraphs at `chapters/ch-07.md:221` and `:244` exceed the 80-word maximum. **Fix:** split each at the category/rule boundary without adding content.
- **[MEDIUM]** The ch-07 bible append repeats `.env` and `load_dotenv()` concepts already established at `bible.md:49-51`, conflicting with the no-duplication check. **Fix:** retain only genuinely new ch-07 terminology and cross-reference the established entries.

## Cross-cutting findings

- The instructional sequence is coherent: raw HTTP → requests → credentials → timeout → retries → taxonomy → conversation loop.
- The chapter's security prose is stronger than several of its examples. Consolidating key loading around one helper is the smallest way to make the examples and prose agree.
- The chapter says every HTTP client can hang without a timeout (`chapters/ch-07.md:153`), but provider SDKs already have defaults; the actionable rule “always pass an explicit timeout” is sound, while “can hang indefinitely” should be scoped to the raw clients documented that way.

## Out-of-scope observations

- `environment.md:85` still says ch-07 examples are “Not yet” tested, despite the ledger and manuscript self-critique claiming tests. This dispatch forbids editing it; synchronize it during the fix pass.
- The style guide's runnable-check convention asks for expected output in a fenced block and a 5–20-line check (`style-guide.md:53-59`); the chapter's final check is substantially longer and gives expected output as prose (`chapters/ch-07.md:321-372`). The dispatch specifically required spot-checking that demo, so this is reported as a non-counted process observation rather than another blocker.

## Honest assessment

The chapter is structurally sound and teaches the right concepts in a useful order. It is not ready for line editing because its credential examples contradict its security lesson, and two retry edge cases make the promised four-bucket behavior incomplete. These are localized fixes rather than a plan failure.

## Self-critique

- **Did I do my job?** Yes. I read the chapter, outline, style guide, bible, ledger, environment, research log, and review rules; inspected installed package signatures; executed the exact TEST-NET block; and ran a fresh UTF-8 decode.
- **What might I have missed?** I did not make live authenticated provider calls because no API keys are configured. I did not execute every illustrative fragment independently because several intentionally depend on names introduced in surrounding snippets.
- **What did I assume without evidence?** I treated the supplied word count as authoritative rather than redefining markdown word-count semantics. Cross-platform TEST-NET behavior outside Windows was not locally executable and is therefore not claimed as independently proven.
