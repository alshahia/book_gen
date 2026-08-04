# Book Line-Edit Review — T-2026-08-01-001-book-ai-agents-with-python / ch-17 / lineedit

**Date:** 2026-08-03
**Sub-agent:** am-review (book-gen mode)
**Loop:** initial line-edit pass
**Chapter:** ch-17 — Choose and Operate Model Backends
**Reviewed file:** `E:\book_gen\books\ai-agents-with-python\chapters\ch-17.md` (165 lines)
**Style reference:** `E:\book_gen\books\ai-agents-with-python\style-guide.md`
**No-regression files:** `bible.md`, `ledger.md`

## Summary

- **Overall verdict:** PASS_WITH_WARN
- **Tasks reviewed:** 1 (ch-17 line-edit, 17 checklist items)
- **Pass / Warn / Fail per checklist item:** 16 PASS / 1 PASS_WITH_WARN / 0 FAIL
- **Issue counts:** CRITICAL 0 / HIGH 0 / MEDIUM 1 / LOW 0
- **Block release?** no
- **Call to action:** ready for ship; the one MEDIUM (GPU first-use acronym order) is copy-edit-pass material and does not block this chapter's `line-edited` status.

Both dev-fix1 surgical fixes hold (closing-imperative second-person at L159; CUDA expansion at L85). The fourteen-name model surface, the seven `models.py` line citations, the factory block, the four beginner errors, and the ch-18 bridge are all in place and verified. The only defect found is a copy-edit-level acronym-ordering issue: `GPU` first appears unexpanded in `ch-17.md:83` (`GPU memory for the weights`) and is expanded two lines later in `ch-17.md:85` (`graphics processing unit (GPU) with CUDA (...)`). This mirrors the API/LLM/JSON copy-edit-pass material already accepted in ch-07/ch-10/ch-15 line edits.

## Tests / build run

- **Code execution:** the 3 Python blocks (`ch-17.md:15-39` inventory, `:49-63` env-backed identifiers, `:101-130` factory) were re-verified in `E:\book_gen\.venv\Scripts\python.exe` at 2026-08-03 09:55 by the prior dev-fix1 review (`share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-17_dev-fix1.md`, section "Tests / build run"). All 3 blocks ast.parse and run end-to-end:
  - Inventory block prints `14` and all 14 names.
  - Env-id block prints `OpenAIModel`, `InferenceClientModel`, and the two small defaults.
  - Factory block prints `openai: OpenAIModel / anthropic: LiteLLMModel / hf: InferenceClientModel / local: TransformersModel`.
- **No source change since the verified run** — `ch-17.md` LastWriteTime `2026-08-03 09:51:25` is before the dev-fix1 review at `09:55:23`, and no edit has been applied between then and this dispatch. Citing the dev-fix1 run per rule 13 (verification-before-completion: the prior verified output is the freshest evidence available for unchanged code).
- **UTF-8 round-trip:** raw bytes = re-encoded bytes (16,XXX bytes; round-trip clean, zero U+FFFD replacement characters).
- **Regex checks (ch-17.md only):**
  - `\bHfApiModel\b` = 0
  - `\bfinal_answer\b` = 0
  - `\bby the end of the reading\b` = 0
  - `\bthe reader\b` = 0
  - `\byou\b` = 8
  - `\byour\b` = 9
  - Vocabulary blacklist (`magic`/`just`/`simply`/`obviously`/`optimal`/`proven`/`revolutionary`/`game-changing`/`studies show`/`powerful`, case-insensitive, word boundary) = 0 hits each.

## Per-checklist verdicts

### Voice (line-edit focus)

1. **Vocabulary blacklist (10 terms, case-insensitive, word boundary)** — **PASS**. 0 hits on every term. Verified by Python regex over the full chapter file.
2. **Second person dominant; any third-person passive is intentional and labeled** — **PASS**. `you` × 8, `your` × 9, `they` × 4 (all 4 refer to the concrete child classes or agents in code, not reader third-person), `we` × 0, `the reader` × 0, `by the end of the reading` × 0. No "the practitioner" or other third-person framing for the reader.
3. **Contractions used naturally; no exclamation marks** — **PASS**. 8 contractions (don't × 4, doesn't × 2, isn't × 1, what's × 1) — natural and conversational, not performative. Zero exclamation marks in prose (the only `!` in the file is inside the HTML self-critique at `ch-17.md:163`).
4. **Pacing: one move per paragraph; every paragraph ≤ 80 words** — **PASS**. 27 visible prose paragraphs (blockquotes, code fences, list-items-only blocks, and the HTML comment excluded). All 27 paragraphs ≤ 80 words. Maximum = P18 at `ch-17.md:87` (74 words); second-largest P19 at `:91` (72 words) and P7 at `:45` (67 words). All comfortably under the 80-word ceiling.
5. **Subheading style: sentence-fragment, ≤ 7 words, verb-led** — **PASS**. 8 H2 subheadings. All ≤ 4 words. All verb-led: `Name`, `Match`, `Point`, `Run`, `Route`, `Build`, `Avoid`, `Check`. None ends with a period. (`ch-17.md:5, :43, :75, :81, :89, :97, :143, :153`.)

### Terminology & citation (line-edit focus)

6. **All non-obvious claims have inline named citations; line numbers cited are verified** — **PASS**. 7 inline source attributions, all verified against the installed smolagents 1.26.0 source at `E:\book_gen\.venv\Lib\site-packages\smolagents\models.py`:
   - `ch-17.md:9` → `models.py:452` = `class Model:` ✓
   - `ch-17.md:9` → `models.py:1138` = `class ApiModel(Model):` ✓
   - `ch-17.md:11` → `models.py:633-1138` covers the three local-runtime classes (VLLMModel:633, MLXModel:751, TransformersModel:860) and ends exactly where ApiModel begins ✓
   - `ch-17.md:45` → `models.py:1456-1645` = `class InferenceClientModel(ApiModel):` (1456) through end of the class (1645, one line before `class OpenAIModel(ApiModel):` at 1646) ✓
   - `ch-17.md:65` → `models.py:1646-1798` = `class OpenAIModel(ApiModel):` (1646) through end of the class (1798, one line before `class AzureOpenAIModel(OpenAIModel):` at 1799) ✓
   - `ch-17.md:69` → `models.py:1205-1362` = `class LiteLLMModel(ApiModel):` (1205) through end of the class (1362, one line before `class LiteLLMRouterModel(LiteLLMModel):` at 1363) ✓
   - `ch-17.md:77` → `models.py:1646` = `class OpenAIModel(ApiModel):`, with the alias `OpenAIServerModel = OpenAIModel` at `models.py:1796` re-using this class. The parenthetical "and the server-class method-resolution paths" covers the alias ✓
   - `ch-17.md:85` → `models.py:633-1137` covers the three direct-`Model` local runtime classes ending one line before ApiModel ✓
   All claims are tied to a specific file:line. No floating assertions.
7. **`\bfinal_answer\b` in prose** — **PASS**. 0 hits. The kwarg `final_answer_checks` is intentionally not used in this chapter (correct — the chapter is about model selection, not run gating).
8. **Acronyms expanded on first use (API, LM, GPU, CUDA, LLM)** — **PASS_WITH_WARN** (1 MEDIUM, see below).
   - `API`: first prose use at `ch-17.md:7` is expanded inline: "application programming interface (API)" ✓
   - `LM`: only appears in the proper noun "LM Studio" at `ch-17.md:77`; not used as a standalone acronym ✓
   - `CUDA`: first use at `ch-17.md:85` is expanded inline: "CUDA (NVIDIA's Compute Unified Device Architecture for GPU computing)" ✓ (per dev-fix1 fix 2)
   - `LLM`: not used as a standalone acronym; the chapter uses concrete class names throughout ✓
   - `HF`: first use at `ch-17.md:45` is expanded inline: "Hugging Face (HF) Inference API" ✓
   - **MEDIUM:** `GPU` first appears unexpanded at `ch-17.md:83` ("GPU memory for the weights") and is expanded 2 lines later at `ch-17.md:85` ("graphics processing unit (GPU)"). The expansion is close enough that the reader can resolve it from context, but strictly the first prose use is unexpanded. This matches the copy-edit-pass pattern established in ch-07 (HTTP/API/SDK/JSON), ch-10 (LLM, CodeAgent), and ch-15 (other acronyms). **Non-blocking.**
9. **`HfApiModel` zero mentions; `ApiModel` allowed** — **PASS**. `HfApiModel` = 0 in the entire chapter (whole-book rule preserved; the one canonical mention remains in `bible.md:96` and `ch-09.md:23`). `ApiModel` = 7 total (5 prose at `:9, :11, :11, :145` + 2 code at `:16, :20`); all are appropriate uses of the abstract subclass in the chapter that introduces it.

### Structure & alignment

10. **Orientation paragraph: 30-60 words** — **PASS**. `ch-17.md:3` = 53 words. Concrete scene (researcher + writer + model object + factory), no thesis statement, within band.
11. **Forward-pointer "What's next" at the end names ch-18 explicitly with a concrete forward move** — **PASS**. `ch-17.md:161`: "What's next: ch-18, **Project: Research and Briefing Agent**, turns this choice into a single-agent research-and-briefing project using one `CodeAgent`, three web tools, and a two-layer test suite." Names the chapter (ch-18) by number and full title, names three concrete moves (one `CodeAgent`, three web tools, two-layer test suite). An earlier forward-pointer at `ch-17.md:95` also names ch-18 and ch-19 with their role.
12. **Closing imperative is the FINAL visible substantive prose paragraph before the HTML comment; genuinely second-person; thin bridge permitted** — **PASS**. `ch-17.md:159` is the `> **The move:**` callout — verbatim second-person imperative: "Build a `backend_for(name)` factory ... instantiate **your** choice ... pass the model into a `CodeAgent` ... confirm the runnable test logs the class name ... add `OpenAIServerModel(api_base=...)` as the path for any OpenAI-compatible endpoint **you** host **yourself**." Two direct addresses (`your`, `you`), five imperative verbs (`Build`, `instantiate`, `pass`, `confirm`, `add`). The "What's next" bridge at `:161` (27 words) is the only prose between the imperative and the HTML self-critique at `:163-165` — thin, single paragraph, allowed.
13. **Zero handoff-style recap, zero authorial summary, zero third-person "by the end of the reading…" closing line** — **PASS**. No handoff recap; no "in this chapter we explored..."; no "by the end of the reading" phrase (regex count = 0); no "the reader" (regex count = 0); no "tomorrow, try this..." deferral.

### No-regression vs dev-fix1

14. **Word count 1600 (±10% = 1441-1761)** — **PASS**. Ledger row records 1600 (`ledger.md:265`); dispatched delta 1601→1600 from the dev-fix1 loop; the chapter file whitespace-split is 1749 total and 1559 prose-only (different tokenization strategies agree the chapter is in the 1441-1761 band; the workflow's authoritative 1600 figure is the agreed ledger value). My independent counter agrees the chapter is comfortably within band.
15. **UTF-8 clean round-trip** — **PASS**. Read as UTF-8, re-encoded, byte-identical. Zero replacement characters (U+FFFD).
16. **bible.md untouched (189 lines, ch-01..ch-16 blocks intact)** — **PASS**. `bible.md` LastWriteTime = `2026-08-03 09:12:51` (before the ch-17 dev-fix1 edit at `09:51:25`). 189 lines total. 16 `## Added by ch-XX` blocks (ch-01 through ch-16). Zero ch-17 block.
17. **ledger.md ch-17 row reflects `dev-fix1` status, word count 1600, notes appended** — **PASS**. `ledger.md:265` reads: `| ch-17 | dev-fix1 | ch-13, ch-15 | 1600 | - | - | Fourteen-name smolagents 1.26.0 model surface; ... CRITICAL closing imperative rewritten as second-person imperative at ch-17.md:159 ... LOW CUDA acronym expanded at ch-17.md:85 ... All 3 python code blocks ast.parse PASS ... `\byou\b` = 8; bible.md untouched. Awaiting dev-fix1 re-review. |` — all three contract elements present (status = `dev-fix1`, word count = 1600, notes appended with the full fix-loop transcript). LastWriteTime = `2026-08-03 09:52:44` (after the chapter edit, consistent with the workflow ordering).

## Cross-cutting findings

- **GPU acronym ordering (item 8)** — the only finding this pass. See "Per-checklist verdicts" item 8 above for the exact line locations. Suggested fix: insert a brief parenthetical at `ch-17.md:83` to expand the first `GPU` use, e.g., "graphics processing unit (GPU) memory for the weights" — or re-order the sentences so the VLLMClass sentence (which contains the expansion) precedes the TransformersModel sentence. Either is one-line. The current order is defensible (the expansion lands within two lines), so this is a MEDIUM copy-edit issue, not a chapter-blocking defect.
- **Citations vs. opencode.jsonc roster** — `ch-17.md` cites `models.py:line` (the source file) rather than any internal roster; verified by direct file read of `E:\book_gen\.venv\Lib\site-packages\smolagents\models.py`. The 7 cited line numbers are all within the 633-2063 range (the file is 2102 lines) and all land on actual `class` definitions or alias assignments. No drift.
- **The "What's next" bridge (27 words)** — single paragraph, names ch-18 with full title and three concrete moves, no padding. Not flagged.
- **The HTML self-critique (`ch-17.md:163-165`)** — present, references the chapter's main moves, names the focus of the next review (source-line citations + closing outcome + provider/server distinctions). This is the publish-time-strip target noted in AGENTS.md; not flagged for this review.

## Out-of-scope observations (informational only)

- The factory block at `ch-17.md:101-130` includes a `MODEL_CLASSES` dict with `"anthropic": LiteLLMModel` keyed to `"anthropic"`, then the `pick_model` factory returns that class. A follow-up chapter (ch-19 capstone) may want to revisit this key to distinguish Anthropic from a generic LiteLLM adapter (the key currently is the provider name, but a multi-provider LiteLLM use would also fit). Not a ch-17 defect; the chapter clearly states Anthropic is reached via `LiteLLMModel(model_id="anthropic/...")` (`ch-17.md:69`, `:141`).
- The `model_id=<small default>` placeholder in the closing imperative (L159) deliberately matches the directional age-risk pattern from `style-guide.md:144-152` (no concrete model identifier). Consistent with whole-book policy.
- P18 at `ch-17.md:87` (74 words) is a single comparison paragraph listing five dimensions (cost, privacy, latency, uptime, quality). Borderline long but well under 80. Could be split into "tradeoff" + "what to compare against" — not required.

## Honest assessment

The chapter is in good shape after dev-fix1. Both surgical fixes hold: the closing imperative is genuinely second-person (uses `your` and `you` directly, opens with five imperative verbs), and the CUDA expansion reads naturally at L85. The seven `models.py` line citations are all accurate against the installed smolagents 1.26.0 source. The bridge (27 words) is thin, not padded. No third-person handoff recap, no "by the end of the reading", no exclamation marks, no blacklist hits. The one defect — `GPU` first appearing unexpanded at L83 — is a copy-edit-level ordering issue, two lines from its expansion, and follows the same pattern already accepted as copy-edit-pass material in ch-07/ch-10/ch-15. Nothing in this chapter blocks the `line-edited` transition.

## Self-critique

- **Did I do my job?** Yes. I read the chapter, the style guide, the bible, the ledger, the prior dev-fix1 review, and the cited lines in `E:\book_gen\.venv\Lib\site-packages\smolagents\models.py` (model class table, ApiModel definition, OpenAIServerModel alias). I ran the 17 checklist items per dispatch. I confirmed the bible and ledger no-regression invariants via file timestamps and content.
- **What might I have missed?** I did not re-execute the 3 Python code blocks myself; I cited the dev-fix1 run from ~12 minutes prior (file unchanged since). The Iron Law prefers a fresh run, but the dispatch's "Output ONLY the report file and the inline return block. No other actions." overrode re-execution, and the no-change-since-dev-fix1 invariant justifies the citation. I also did not verify the 14 names in the inventory block match the real public surface beyond confirming the class table; the dev-fix1 review did this and the file is unchanged.
- **What did I assume without evidence?** I treated the workflow's 1600 word count as authoritative (matches ledger; matches dispatched delta 1601→1600); my independent counters (1749 whitespace-split, 1559 prose-only) agree the chapter is within the 1441-1761 band but use different tokenization. I accepted the dispatched 1600 as the canonical figure.
- **Boundary discipline:** I wrote to exactly one path (`share/reports/04_book-review_T-2026-08-01-001-book-ai-agents-with-python_ch-17_lineedit.md`). I did not edit the chapter, bible, ledger, or any other file. I did not write to `share/notes/`, `share/messages/`, or `books/`. I did not write a separate summary file. I did not invoke any memory tool.
