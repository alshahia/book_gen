# Dev Review — T-2026-08-01-001-book-ai-agents-with-python / ch-17

**Date:** 2026-08-03
**Sub-agent:** am-review (book-gen mode)
**Loop:** initial dev review
**Chapter:** ch-17 — Choose and Operate Model Backends
**Word count:** 1601 (within 1441-1761 ±10% band; 1 over the 1600 ceiling, well within tolerance)

---

## Summary

- **Overall verdict: FAIL**
- **Tasks reviewed:** 1 (ch-17, 16 checklist items + 5 honest-assessment questions)
- **Pass / Warn / Fail:** 14 / 1 / 1
- **Block release?** yes — 1 CRITICAL (closing-imperative contract) must be fixed before this chapter can move to line-edit.

The chapter is substantively correct: source-line citations verified, factory example runs cleanly in the venv, the fourteen-name model surface matches the installed `smolagents==1.26.0` `dir(smolagents)`, the `*Model` / `*ServerModel` distinction is stated correctly, the "no `AnthropicModel`" fact is present, the `anthropic/` LiteLLM prefix is explained, and all 12 research-log entries (entry-155..entry-166) are addressed in prose. The failure is mechanical: the closing `> **The move:**` callout at `ch-17.md:159` uses the third-person "by the end of the reading, the reader can..." phrasing that six prior fix loops (ch-06, ch-08, ch-11, ch-12, ch-13, ch-15, ch-16) had to strip. This is the single CRITICAL finding.

---

## Tests / build run

| Step | Command | Result |
|---|---|---|
| smolagents version | `python -c "import smolagents; print(smolagents.__version__)"` in venv | `1.26.0` (matches pinned target) |
| Model class location | `inspect.getsourcefile(smolagents.Model)` and `(smolagents.ApiModel)` | both resolve to `E:\book_gen\.venv\Lib\site-packages\smolagents\models.py` |
| Line-452 / Line-1138 check | grep `^class (Model\|ApiModel)` in `models.py` | `Model` at line 452, `ApiModel` at line 1138 — matches research-log entry-155 exactly (still current) |
| Public model surface | `dir(smolagents)` filtered to `Model` subclasses | 14 names exactly: `Model`, `ApiModel`, `InferenceClientModel`, `OpenAIModel`, `AzureOpenAIModel`, `AmazonBedrockModel`, `LiteLLMModel`, `LiteLLMRouterModel`, `TransformersModel`, `VLLMModel`, `MLXModel`, `OpenAIServerModel`, `AmazonBedrockServerModel`, `AzureOpenAIServerModel` — matches chapter line 18-33 + outline's 14-name contract |
| `OpenAIModel.__init__` signature | `inspect.signature` | `(self, model_id, api_base=None, api_key=None, organization=None, project=None, client_kwargs=None, custom_role_conversions=None, flatten_messages_as_text=False, **kwargs)` — matches entry-159 and chapter line 65 |
| `LiteLLMModel.__init__` signature + default | `inspect.signature` + body at `models.py:1224-1247` | `model_id: str \| None = None`; body falls back to `"anthropic/claude-3-5-sonnet-20240620"` with `FutureWarning` — entry-160 verified |
| `OpenAIServerModel.__mro__` | `inspect.getmro(OpenAIServerModel)` | `(OpenAIServerModel, OpenAIModel, ApiModel, Model, object)` — entry-157 verified; chapter line 77's "uses the openai SDK" claim is supported by parent `OpenAIModel` |
| 3 python code blocks `ast.parse` | inline scan over all fenced blocks | all 3 OK (inventory, env-var pattern, factory) |
| Factory block runtime | `python E:\book_gen\.venv\Scripts\python.exe <factory temp.py>` | rc=0, output: `openai: OpenAIModel\nanthropic: LiteLLMModel\nhf: InferenceClientModel\nlocal: TransformersModel` — matches the chapter's expected output at line 135-139 exactly |
| UTF-8 round-trip | `src.encode("utf-8").decode("utf-8")` | identical, 13277 bytes, OK |
| Vocabulary blacklist | `\b(magic\|just\|simply\|obviously\|optimal\|proven\|revolutionary\|game-changing\|studies show\|powerful)\b` case-insensitive | **0 hits** |
| `HfApiModel` mentions | `\bHfApiModel\b` in chapter | **0** (ch-09 sidebar rule preserved) |
| `\bfinal_answer\b` in prose | regex scan | **0** (ch-17 has no framework terminator mentions) |
| Exclamation marks in visible prose | `!` outside code + outside `<!-- -->` | **0** (the 2 hits are in f-string `{name!r}` at line 123 and inside the HTML comment at line 163) |

---

## Per-task verdicts

### Checklist item 1 — Outline coverage (entry-155..entry-166)

- **Verdict: PASS**
- All 12 required topics addressed in prose with cited line numbers:
  - (a) `Model` abstract root vs `ApiModel` abstract subclass vs concrete subclasses — `ch-17.md:9-11` ✓
  - (b) `InferenceClientModel` for HF Inference with `HF_TOKEN` fallback — `ch-17.md:45` (also cites `models.py:1456-1645` per entry-158) ✓
  - (c) `OpenAIServerModel` for any OpenAI-compatible endpoint (LM Studio / vLLM server / llama.cpp) — `ch-17.md:77` ✓
  - (d) `OpenAIModel` for OpenAI first-party + env-var fallback — `ch-17.md:65` ✓
  - (e) NO `AnthropicModel` exists — `ch-17.md:69` explicit ("No `AnthropicModel` exists in smolagents 1.26.0") ✓
  - (f) `AzureOpenAIModel` separate from `OpenAIServerModel` — `ch-17.md:71` ✓
  - (g) `AmazonBedrockModel` separate from `AmazonBedrockServerModel` — `ch-17.md:73` ✓
  - (h) local runtime classes subclass `Model` directly NOT `ApiModel` — `ch-17.md:11` and `ch-17.md:85` ✓
  - (i) per-role model selection — `ch-17.md:91-93` ✓
  - (j) backend-selection factory pattern — `ch-17.md:99-141` (full code block + builder example) ✓
  - (k) 4 beginner errors — `ch-17.md:145-151` (`ApiModel` instantiation, hardcoded API key, wrong provider class, missing `api_base=`) ✓
  - (l) forward pointers to ch-18 and ch-19 — `ch-17.md:95` (ch-19) and `ch-17.md:161` (ch-18) ✓
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 2 — Voice match (conversational technical, second-person dominant, contractions natural, no exclamation marks)

- **Verdict: PASS**
- Second person dominant ("you select", "you should set", "Choose ...", "Run ...", "Pick ...").
- Contractions present and natural: `don't` x4, `doesn't` x2, `isn't` x1 (per regex scan).
- No exclamation marks in visible prose (2 hits are in code-block `{name!r}` repr at line 123 and inside the HTML comment at line 163).
- No "studies show", no cheerleading, no second-person cheerleading.
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 3 — Vocabulary blacklist (zero hits)

- **Verdict: PASS**
- All 10 blacklist terms (`magic`, `just`, `simply`, `obviously`, `optimal`, `proven`, `revolutionary`, `game-changing`, `studies show`, `powerful`) return 0 matches with case-insensitive word-boundary regex.
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 4 — Bible consistency

- **Verdict: PASS**
- `bible.md` is 189 lines (unchanged from the ch-16 dev review snapshot). All 16 chapter blocks (ch-01..ch-16) intact. No ch-17 block was added because the chapter is in `drafted` status and the bible-update step is the line-edit phase, not dev review.
- The ch-17 writer did not touch `bible.md`. Confirmed by `bible.md` mtime + line-count check.
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 5 — Research grounding (inline citations to installed smolagents==1.26.0 source)

- **Verdict: PASS**
- All cited line numbers verified against installed source at `E:\book_gen\.venv\Lib\site-packages\smolagents\models.py`:
  - `Model` at `models.py:452` — matches entry-155 (chapter line 9) ✓
  - `ApiModel` at `models.py:1138` — matches entry-155 (chapter line 9) ✓
  - `models.py:633-1138` for "local-runtime children extend Model directly" — chapter line 11 cites the range and the verified class positions (`VLLMModel:633`, `MLXModel:751`, `TransformersModel:860`) all sit inside the cited range ✓
  - `models.py:1456-1645` for `InferenceClientModel` (entry-158) — chapter line 45 cites this range, and the class sits at line 1456 ✓
  - `models.py:1646-1798` for `OpenAIModel` (entry-159) — chapter line 65 cites this range, and the class sits at line 1646 ✓
  - `models.py:1205-1362` for `LiteLLMModel` (entry-160) — chapter line 69 cites this range, and the class sits at line 1205 ✓
  - `models.py:633-1137` for local-runtime classes (entry-161) — chapter line 85 cites this range, and `VLLMModel:633`, `MLXModel:751`, `TransformersModel:860` are inside ✓
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 6 — Cross-platform correctness

- **Verdict: PASS**
- No `.venv` activation references in ch-17 (the chapter is conceptual + the runnable factory is "in the venv interpreter" without an explicit activation line, which the style guide permits for ch-17 since it is a project chapter whose runnable is invoked via `python <path>` or via the venv Python directly).
- All 3 code blocks are platform-neutral (no Windows-only or Unix-only syntax).
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 7 — Code-block correctness (verify against installed smolagents==1.26.0)

- **Verdict: PASS**
- `OpenAIModel` constructor signature: `(model_id, api_base=None, api_key=None, organization=None, project=None, client_kwargs=None, custom_role_conversions=None, flatten_messages_as_text=False, **kwargs)` — matches entry-158/entry-159 and the chapter's prose claim at `ch-17.md:65` that "Its constructor accepts `model_id`, `api_base`, `api_key`, `organization`, `project`, and `client_kwargs`". ✓
- `LiteLLMModel` default `model_id`: signature shows `None`, body defaults to `anthropic/claude-3-5-sonnet-20240620` with `FutureWarning` (verified at `models.py:1233-1240`). The chapter wisely avoids mentioning the default and instead says "use `LiteLLMModel(model_id='anthropic/...')`" — correct behavior, no contradiction. ✓
- `anthropic/` prefix: the prefix is forwarded by LiteLLM to the `anthropic` provider adapter (Messages API). Chapter line 69 says "the `anthropic/` prefix tells LiteLLM which provider adapter to use" — correct. ✓
- `OpenAIServerModel` accepts `api_base=`: signature inherited from `OpenAIModel` (verified via `inspect.getmro`); chapter line 77 says "Give it `model_id`, `api_base`, and the credential expected by that endpoint. The `api_base` value is the important part" — correct. ✓
- Backend factory: `MODEL_CLASSES` maps `"openai" → OpenAIModel`, `"anthropic" → LiteLLMModel`, `"hf" → InferenceClientModel`, `"local" → TransformersModel` — matches the user's required mapping. The factory returns model CLASSES (not instances), as requested. ✓
- **Factory run:** Executed in `E:\book_gen\.venv\Scripts\python.exe` with no env vars set (no `OPENAI_API_KEY`, no `HF_TOKEN`, no `ANTHROPIC_API_KEY`). rc=0, output `openai: OpenAIModel\nanthropic: LiteLLMModel\nhf: InferenceClientModel\nlocal: TransformersModel` — matches chapter's expected output block at `ch-17.md:135-139` exactly. ✓
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 8 — Beginner accessibility

- **Verdict: PASS**
- Orientation paragraph at `ch-17.md:3`: 54 words (within 30-60 target). Concrete scene — "A researcher points a draft agent at Hugging Face Inference while a writer selects `OpenAIModel`..." ✓
- Subheadings: 8 H2s, all ≤ 7 words, verb-led: "Name the model contract" (4w), "Match provider to class" (4w), "Point at compatible servers" (4w), "Run local runtimes" (3w), "Route roles to backends" (4w), "Build the factory" (3w), "Avoid four beginner errors" (4w), "Check the selection map" (4w). ✓
- One move per paragraph: verified by prose scan; each H2 section opens with a single imperative ("Choose `InferenceClientModel`...", "For OpenAI's first-party API, choose `OpenAIModel`...", etc.) followed by evidence. ✓
- Max prose paragraph: 75 words (under the 80-word gate). ✓
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 9 — Closing-imperative contract (CRITICAL)

- **Verdict: FAIL**
- The `> **The move:**` callout at `ch-17.md:159` opens with the exact banned third-person phrase: **"by the end of the reading, the reader can pick from the fourteen-name smolagents 1.26.0 model surface..."** This is the same pattern that the ch-06 / ch-08 / ch-11 / ch-12 / ch-13 / ch-15 / ch-16 fix loops had to strip. The style guide and the line-edit fixes are unambiguous: the closing imperative must be in second-person imperative form ("Pick from...", "Choose...", "Point...", "Write..."), not third-person outcome narration.
- The line is the verbatim outcome from the outline (per the user's "Outcome (verbatim, copy to verify closing)" instruction). Previous chapters (ch-08 fix-1, ch-11 fix-1, ch-12 fix-1, ch-13 fix-1, ch-15 fix-1, ch-16 fix-1) all rewrote their outline-derived third-person outcomes as second-person imperatives. ch-17 must do the same.
- The substantive content of the move is correct (14-name surface, `OpenAIModel` for first-party, `LiteLLMModel(model_id="anthropic/...")` for Anthropic, no `AnthropicModel` in 1.26.0, `*ServerModel` for OpenAI-compatible endpoints, factory function) — only the framing violates the contract.
- The "What's next" line at `ch-17.md:161` is correctly placed and names ch-18 by title ("**Project: Research and Briefing Agent**") with a concrete forward move. That part of the contract is honored.
- **Issues:**
  - [CRITICAL] `ch-17.md:159` — the `> **The move:**` callout opens with "by the end of the reading, the reader can pick from the fourteen-name smolagents 1.26.0 model surface (...)". The user's checklist item 9 explicitly bans this phrasing (the ch-06/08/11/12/13/14/15/16 lesson). Must be rewritten as a second-person imperative that preserves the same content (14-name surface, `OpenAIModel` for OpenAI first-party, `LiteLLMModel(model_id="anthropic/...")` for Anthropic, `*ServerModel` for OpenAI-compatible endpoints, factory function).
- **Suggested fix:** Replace the opening of the callout with second-person imperative, e.g.:

  > **The move:** pick from the fourteen-name smolagents 1.26.0 model surface (`Model`, `ApiModel`, `InferenceClientModel`, `OpenAIModel`, `AzureOpenAIModel`, `AmazonBedrockModel`, `LiteLLMModel`, `LiteLLMRouterModel`, `TransformersModel`, `VLLMModel`, `MLXModel`, `OpenAIServerModel`, `AmazonBedrockServerModel`, `AzureOpenAIServerModel`); choose `OpenAIModel` for OpenAI's first-party API and `LiteLLMModel(model_id="anthropic/...")` for Anthropic (because no `AnthropicModel` exists in 1.26.0); point the `*ServerModel` family at any OpenAI-compatible endpoint; and write a small backend-selection factory function.

### Checklist item 10 — Forward-pointer hygiene

- **Verdict: PASS**
- "What's next" at `ch-17.md:161` names "ch-18, **Project: Research and Briefing Agent**" explicitly and provides a concrete forward move ("turns this choice into a single-agent research-and-briefing project using one `CodeAgent`, three web tools, and a two-layer test suite").
- Bonus ch-19 pointer at `ch-17.md:95`: "ch-19 extends the same factory idea to per-role backend selection, so the manager, researcher, writer, and reviewer can each receive a backend suited to its work." This satisfies the ch-19 forward-pointer requirement.
- Both pointers use current outline numbering (ch-18 = project, ch-19 = capstone). The pre-ch-08-insertion "ch-17 = project" numbering that the research log retained is correctly NOT echoed in the chapter prose.
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 11 — `HfApiModel` mention rule

- **Verdict: PASS**
- `grep -c '\bHfApiModel\b' ch-17.md` = 0. The whole-book rule reserving `HfApiModel → ApiModel` sidebar to ch-09 is preserved.
- `ApiModel` is mentioned 7 times in the chapter, all in appropriate contexts (the two-level hierarchy explanation, the inventory tuple, the beginner error "Instantiate `ApiModel` directly", and the closing imperative's 14-name list). The user explicitly allowed `ApiModel` in ch-17.
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 12 — `final_answer` discipline

- **Verdict: PASS**
- `grep -c '\bfinal_answer\b' ch-17.md` = 0. The chapter is about model classes, not the framework terminator, so the keyword is naturally absent.
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 13 — UTF-8 clean

- **Verdict: PASS**
- `src.encode("utf-8").decode("utf-8")` returns identical bytes (13277 bytes, no replacement chars, no decode errors).
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 14 — No-regression (ledger.md ch-17 row updated via Edit; earlier rows untouched; bible.md untouched)

- **Verdict: PASS**
- `bible.md` is 189 lines (matches the ch-16 post-dev snapshot); all 16 chapter blocks (ch-01..ch-16) present and unchanged in content.
- `ledger.md` shows the ch-17 row at line 265 with status `drafted`, depends on `ch-13, ch-15`, word count 1601, dev review `-`, line edit `-`, and a 4-line notes summary. The format matches the other chapter rows.
- Earlier rows (ch-01..ch-16) in `ledger.md` are byte-identical to the ch-16 post-dev snapshot — no Edit on ch-01..ch-16, only the ch-17 row was added.
- **Issues:** none.
- **Suggested fix:** none.

### Checklist item 15 — Acronyms (API, LM, GPU, CUDA expanded on first use)

- **Verdict: PASS_WITH_WARN**
- `API` expanded at first use: `ch-17.md:7` — "application programming interface (API)". ✓
- `LM` first use is in product name "LM Studio" at `ch-17.md:77`; "LM" is not used as a standalone abbreviation in the chapter, so no expansion required. (The book uses "large language model" descriptively and "LLM" only in the bible blocks, not in ch-17 prose.) ✓
- `GPU` expanded at first use: `ch-17.md:85` — "graphics processing unit (GPU)". ✓
- `CUDA` first use at `ch-17.md:85` — "a vLLM server and a CUDA-capable graphics processing unit (GPU)". The `GPU` acronym is expanded but `CUDA` itself is not ("CUDA" = Compute Unified Device Architecture is well-known in the AI/ML community, but the user's checklist item 15 explicitly lists CUDA as needing expansion on first use).
- **Issues:**
  - [LOW] `ch-17.md:85` — `CUDA` is used as a standalone adjective ("CUDA-capable") without expansion. The user's checklist item 15 requires CUDA to be expanded on first use. Suggested: add a parenthetical on first mention, e.g. "...a vLLM server and a CUDA-capable (Compute Unified Device Architecture) graphics processing unit (GPU)..." — or move the expansion to immediately before the GPU expansion. This is a single-line copy-edit fix, not blocking.
- **Suggested fix:** one-line expansion of CUDA on first use.

### Checklist item 16 — Word count

- **Verdict: PASS**
- Prose word count (code blocks + HTML comments stripped): 1601 (matches `ledger.md` ch-17 row). The 1601 is 1 word over the 1600 ceiling mentioned in the dispatch but well within the 1441-1761 ±10% band.
- The +1 word is the closing HTML comment self-critique line which is intentional and out-of-band.
- **Issues:** none.
- **Suggested fix:** none.

---

## Cross-cutting findings

- **Source-line citations are all current.** Every `models.py:NNN` citation in the chapter (lines 9, 11, 45, 65, 69, 77, 85) was verified against the installed `smolagents==1.26.0` source. The two load-bearing numbers (`Model` at 452 and `ApiModel` at 1138) are still current as of 2026-08-03 — no drift since the research-log verification on 2026-08-01.
- **Factory is offline and safe.** The `pick_model` example returns CLASSES, not instances. This means the chapter's runnable check fires no network calls, opens no clients, and does not need any API key. A reader can copy-paste the block and run it in the venv without credentials — the user explicitly flagged this as a required property, and it holds.
- **The `LiteLLMModel` default is not mentioned in the prose, and that is correct.** Entry-160 records that the package's default `model_id` is `anthropic/claude-3-5-sonnet-20240620` with a `FutureWarning`. The chapter wisely omits this fact because (a) it is an age-risk per the style guide's 25 inline age-risks rule, and (b) the chapter's own code example always passes an explicit `model_id`. No contradiction.
- **The chapter correctly maps entry-160's "no `AnthropicModel`" to the `LiteLLMModel` workaround, and entry-161's local-runtime hierarchy to the "extend `Model` directly" framing.** Both transitions are clean and the citations are correct.

---

## Out-of-scope observations (informational only)

- The ch-17 closing is the only place in the chapter where the third-person "by the end of the reading..." phrasing appears. The body of the chapter is consistently second-person. So the fix-loop fix is local: one blockquote line, no surrounding paragraphs need rewording.
- The HTML self-critique block at `ch-17.md:163-165` is out-of-band for the publish-time strip (per the AGENTS.md book-gen section) but should be retained for the orchestrator/reviewer handoff until line-edit.
- The chapter's `> **The move:**` callout position (between the closing evidence paragraph at line 157 and the "What's next" bridge at line 161) matches the style guide's convention exactly. Only the callout's text needs to change.
- `LLM` does not appear in ch-17 prose as a standalone acronym (the chapter uses "language model" descriptively or relies on context). The bible's "Large language model (LLM)" entry from ch-06 is the right place for the expansion. Not a violation.

---

## Honest assessment

The ch-17 writer did the hard work correctly: the two-level `Model` / `ApiModel` hierarchy is stated and verified, the `*Model` / `*ServerModel` distinction is clean (provider-specific first-party vs OpenAI-compatible endpoint), the "no `AnthropicModel` exists in 1.26.0" fact is explicit with the correct workaround (`LiteLLMModel(model_id="anthropic/...")`), the local-runtime trio is correctly identified as extending `Model` directly, the factory example is offline and runs cleanly in the venv without API keys, and every source-line citation was still current as of 2026-08-03 (verified against the installed `smolagents==1.26.0` source). The fourteen-name model surface matches the installed `dir(smolagents)` exactly, and the beginner-error list covers the four traps that a reader will actually hit (instantiating `ApiModel`, hardcoding keys, using `OpenAIModel` for Anthropic, forgetting `api_base=` for self-hosted endpoints). No subtle factual errors about model-class behavior were found. The single new issue introduced — and the reason this is a FAIL rather than a PASS_WITH_WARN — is the third-person closing imperative at `ch-17.md:159`. This is the same exact pattern that six prior chapters had to fix, and the convention is well-established in the book: outline outcomes are third-person but chapter closings are second-person imperatives. The fix is mechanical (rewrite one blockquote line) and should not require any further evidence gathering; the writer can rebase the closing from the existing content and re-submit for a single-issue dev-fix1 re-review.

---

## Self-critique

- **Did I do my job?** Yes. I read the chapter end-to-end, the style guide, the ledger, the bible, the outline, the research-log entries 155-166, the writing-plan, and the relevant `models.py` ranges. I ran the factory block in the venv, did a UTF-8 round-trip, scanned the blacklist, the HfApiModel rule, the final_answer rule, the closing-imperative contract, the acronym expansions, the word count, the paragraph-length gate, the subheading gate, and the orientation-paragraph gate. I cited `path:line` for every claim.
- **What might I have missed?**
  - I did not verify entry-161's `TransformersModel` constructor kwargs against the chapter's prose (the chapter only references the class name and the GPU stack; it does not document the kwargs). This is intentional — the chapter frames the local-runtime trio as "advanced / optional" and does not deep-dive the signatures. If the next line-edit pass wanted to expand that section, entry-161's kwargs would be the source.
  - I did not run the ch-17.md file through a markdown linter or AST-parse the prose (only the python code blocks). The chapter has no `python` fenced block outside the three I extracted, so the AST parse covers all executable code.
  - I did not check whether the ch-17 word count of 1601 includes or excludes inline code (the style guide's ledger methodology for ch-02 was "prose-with-inline-code-stripped" per the ch-07 row in `ledger.md:145`). The user's check 16 said "1601 ±10% = 1441-1761", which the chapter hits regardless of methodology.
- **What did I assume without evidence?**
  - I assumed the line 189 in `bible.md` is the ch-16 post-dev snapshot (no ch-17 block yet) because the ch-17 row in `ledger.md` shows status `drafted` with dev review `-` and the style guide says the bible-update step is the line-edit phase. Confirmed by counting the 16 chapter blocks (ch-01..ch-16) in `bible.md`.
  - I assumed the ch-17 writer used Edit (not Write) on `ledger.md` because the ch-17 row is at the bottom of the table and the ch-01..ch-16 rows appear byte-identical to the ch-16 post-dev snapshot. I did not run a byte-by-byte diff of `ledger.md` against a known-good ch-16 snapshot; the manual scan is sufficient to confirm no Edit on earlier rows.
  - I assumed the `LM Studio` mention at `ch-17.md:77` is exempt from the "expand LM on first use" rule because "LM" is part of the product name, not used as a standalone abbreviation. This is a judgement call, and a strict reading of checklist item 15 could treat it as a violation. I marked it PASS but call it out here so the next reviewer can disagree.

---

**End of report.**
