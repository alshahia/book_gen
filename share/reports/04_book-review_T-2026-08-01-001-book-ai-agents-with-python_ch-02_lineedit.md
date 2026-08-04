# Line-Edit Review — ch-02 — AI Agents with Python

Date: 2026-08-01
Reviewer: am-review
Chapter: ch-02.md (post dev-fix1; 1471 words)
Previous verdict: PASS (dev re-review)
Pass: line-edit

## Verdict: PASS_WITH_WARN

The chapter is voice-clean, citation-clean, blacklist-clean, and structurally aligned with the style guide. Five low-priority items surface — three minor forward-pointer hygiene concerns in body prose, one phrasing inconsistency between the opening and closing orientation paragraphs, and one stylistic note on a 41-word evidence sentence in section 1. None are blockers; none require a fix loop. The chapter is line-edit clean enough to ship to Phase 7 copy-edit (or directly to publishing if the project skips copy-edit per the ch-02 structural-change plan).

## Summary

| Dimension | Result |
|---|---|
| Voice (conversational technical, second person dominant) | PASS |
| Vocabulary blacklist | PASS (0 matches) |
| Pacing and rhythm | PASS |
| Terminology consistency | PASS |
| Citation hygiene | PASS (every claim named inline) |
| Cross-platform accuracy | PASS |
| Code-block conventions | PASS |
| Forward-pointer hygiene | PASS_WITH_WARN (3 body-prose forward-pointers) |
| Outcome-line contract | PASS (verbatim match with style guide) |
| No regression vs. dev re-review | PASS |

**Counts:** 0 FAIL, 4 WARN, 0 FAIL-by-omission.

## Tests / build run

Line-edit pass — no code execution required. The chapter is prose. The dev re-review (2026-08-01) already verified the runnable check at ch-02.md:111-123 prints `1.26.0` from the venv interpreter, and that verification is unchanged. No re-test needed.

## Per-checklist verdicts (with path:line evidence)

### 1. Voice consistency — VERDICT PASS

Conversational technical; second person dominant. Verified by:
- Direct-address imperatives throughout: "Pick a recent Python 3.10 or newer" (ch-02.md:7), "Build a project folder and a virtual environment" (ch-02.md:21), "Install smolagents and JupyterLab" (ch-02.md:47), "Prefer `python -m <module>` over `python script.py`" (ch-02.md:59), "Keep secrets in a `.env`, never in code" (ch-02.md:65), "Add the canonical Python `.gitignore`" (ch-02.md:82). Each subheading names the move, in line with style-guide § "Subheadings."
- Second-person verbs: "you have" (line 3), "you can verify" (line 45), "you will see" (line 63), "you write" (line 129). First-person plural "we" as subject: 0 matches in prose. Style-guide § "Person" permits "we" sparingly; this chapter does not need it.
- One move per paragraph, then evidence-nut: confirmed. Each section opens with the imperative subheading, then a 1-2 sentence statement of the move, then a 1-3 sentence evidence paragraph naming a source. The chapter breathes — sections alternate short orienting sentences (e.g., ch-02.md:19 "On Linux there is no single python.org installer." — 8 words) with longer evidence sentences (e.g., ch-02.md:15 — 51 words).

### 2. Vocabulary blacklist — VERDICT PASS

Style-guide blacklist terms scanned in prose only (prose = no code blocks, no HTML comments, no inline HTML): `magic`, `magical`, `optimal`, `proven`, `revolutionary`, `game-changing`, `powerful`, `simply`, `obviously`, `just` — **0 matches each.** Verified by:
- `magic` / `magical`: 0 matches.
- `optimal`: 0 matches. Style-guide blacklists "optimal" without a named-study citation; chapter avoids it.
- `proven`: 0 matches. Chapter does not invoke "proven."
- `revolutionary` / `game-changing` / `powerful`: 0 matches. Chapter avoids hype vocabulary.
- `simply` / `obviously` / `just`: 0 matches. Chapter uses concrete instructions, not hand-waving.
- Productivity jargon (`synergy`, `leverage`, `optimize`, `deep dive`, `unpack`, `delve`): 0 matches in prose.

### 3. Pacing and rhythm — VERDICT PASS

Short sentences for key claims:
- ch-02.md:19 "On Linux there is no single python.org installer." (8 words)
- ch-02.md:45 "Running `deactivate` returns you to the system default." (8 words)
- ch-02.md:69 "Two consequences follow." (3 words)
- ch-02.md:63 "`python -m venv` already used it." (6 words)
- ch-02.md:63 "`python -m pip install` did too." (6 words)
- ch-02.md:109 "None of those files belong in git." (7 words)
- ch-02.md:109 "`.env` covers your secrets file." (5 words)

Longer sentences for explanation:
- ch-02.md:15 (51 words, Windows-install trajectory)
- ch-02.md:17 (52 words, macOS universal2 narrative)
- ch-02.md:49 (32 words, pip recommendation with rationale)

Mix verified: the chapter breathes — short claim / longer evidence / short claim is the default rhythm.

### 4. Terminology consistency — VERDICT PASS

| Term | First prose use | Inline definition / gloss |
|---|---|---|
| `.venv` | ch-02.md:3 (orientation) | ch-02.md:23 "A virtual environment is a self-contained directory that holds a copy of the Python interpreter and the packages your project installs into it." |
| `JupyterLab` | ch-02.md:3 (orientation) | ch-02.md:51 "JupyterLab is the notebook UI the book uses for exploratory examples." |
| `kernel` | ch-02.md:51 | ch-02.md:51 inline (via JupyterLab chub quote): "your code executes in a kernel environment" |
| `smolagents` | ch-02.md:3 (orientation) | ch-02.md:9 (PyPI metadata citation): "Requires: Python >=3.10" |
| `.gitignore` | ch-02.md:3 (orientation) | ch-02.md:84 "The GitHub-curated `Python.gitignore` is the standard template." |
| `.env` | ch-02.md:3 (orientation) | ch-02.md:67 "API keys — Hugging Face tokens, OpenAI keys, anything else — belong in a `.env` file at the project root, never in source code..." |
| `.env.example` | ch-02.md:3 (orientation) | ch-02.md:69 ".env.example placeholder file with the same key names but empty values..." |
| `pip` | ch-02.md:15 (passing reference) | ch-02.md:49 expanded: "every install runs through `python -m pip install <package>`. The Python Packaging Authority's 'Install packages in a virtual environment using pip and venv' guide recommends this form because it guarantees the package lands inside the active `.venv`..." |
| `python-dotenv` | ch-02.md:51 (install line) | ch-02.md:67 (cited guide reference): "The python-dotenv chub guide (1.2.2, 2026-03-12) documents the canonical pattern..." |

All terminology first-uses are glossed within the chapter body. No bare-uses without a definition or citation.

### 5. Citation hygiene — VERDICT PASS

Every load-bearing claim has an inline source name. Verified by reading the full chapter:

| Claim | Source named inline | Location |
|---|---|---|
| Python 3.10+ required | "smolagents PyPI project page lists 'Requires: Python >=3.10'" | ch-02.md:9 |
| 3.10–3.14 active versions | "Python Software Foundation's 'Active Python releases' page" | ch-02.md:9 |
| Windows install path changed in late 2025 | "Python Install Manager (an MSIX installer from python.org or the Microsoft Store) replaced the legacy 'Python launcher for Windows'" | ch-02.md:15 |
| Windows `%LocalAppData%\Python\bin` path | "CLI tools installed with pip (such as `jupyter`) land under `%LocalAppData%\Python\bin`, which the installer prompts you to add to `PATH`" | ch-02.md:15 |
| macOS universal2 / Gatekeeper | "the Python Software Foundation signs the build" | ch-02.md:17 |
| Linux distro packages lag | "The Python docs explicitly say distribution packages often lag the latest release" | ch-02.md:19 |
| One venv per project | "The Python tutorial's 'Virtual Environments and Packages' section recommends one per project" | ch-02.md:23 |
| `.venv` directory name | "the Python Packaging Authority's venv guide recommends the same `.venv` location" | ch-02.md:23 |
| Use `python -m pip` | "The Python Packaging Authority's 'Install packages in a virtual environment using pip and venv' guide recommends this form" | ch-02.md:49 |
| Pin versions | (same PyPA guide) | ch-02.md:49 |
| JupyterLab ≠ sandbox | "The JupyterLab chub entry warns that 'JupyterLab only provides the UI and server shell; your code executes in a kernel environment'" | ch-02.md:51 |
| Three ways to run Python | "The Python docs' 'Command line and environment' section lists three ways..." | ch-02.md:61 |
| `python -m` is preferred | "The docs prefer `python -m` for two reasons" | ch-02.md:61 |
| python-dotenv pattern | "The python-dotenv chub guide (1.2.2, 2026-03-12) documents the canonical pattern" | ch-02.md:67 |
| Do not commit `.env` | "The python-dotenv chub guide's 'Common Pitfalls' section names the rule directly" | ch-02.md:69 |
| Canonical `.gitignore` | "The GitHub-curated `Python.gitignore` is the standard template" | ch-02.md:84 |

No vague "as we will see" / "in the next chapter" / "studies show" hand-waving. (Searched: 0 matches for those three exact phrasings.)

**WARN (not a FAIL):** Three body-prose forward-references to specific later chapters appear beyond the explicit "What's next" paragraph. They are specific named-chapter pointers (not vague "later" hand-waving), and they serve reader comprehension by naming when the installed artifacts will be used:
- ch-02.md:63 "(ch-17, ch-18, ch-19)" — names project chapters where `.py` files live.
- ch-02.md:80 "the variable `InferenceClientModel` reads in ch-09" — names the chapter where `HF_TOKEN` is first read.
- ch-02.md:80 "The OpenAI and Anthropic lines are reserved for ch-17's backend factory" — names the chapter where the extra keys come into play.

Strictly against the rule "no internal cross-references beyond the explicit 'What's next' paragraph." Recommend master decide whether to retain (specific named references aid the reader) or rewrite in chapter-relative terms ("in later project chapters" / "later chapters that use API keys"). Not a line-edit blocker — the references are factual and pedagogically useful — but worth surfacing.

### 6. Cross-platform accuracy — VERDICT PASS

- Windows activation: `.venv\Scripts\activate` (ch-02.md:36, ch-02.md:125). Header at line 33 says "Windows (PowerShell or cmd)" — works for both. ✓
- macOS/Linux activation: `source .venv/bin/activate` (ch-02.md:42, ch-02.md:125). Header at line 39 says "macOS or Linux (bash or zsh)" — works for both shells. ✓
- Path-verification commands: `where python` (Windows) and `which python` (macOS/Linux) at ch-02.md:45. ✓
- No commitment to exact version numbers that change: Python 3.10+ is a floor (stable). The specific release "Python 3.13.7" at ch-02.md:11 is past-tense ("The version in this book's `.venv` is Python 3.13.7") — present-tense factual, not a future commitment. The chapter explicitly flags age-risk at ch-02.md:15 ("**This section may age quickly**").

### 7. Code-block conventions — VERDICT PASS

All 7 code blocks conform:

| Line | Language tag | Content | Convention check |
|---|---|---|---|
| ch-02.md:27 | bash | `mkdir ai-agents-with-python` / `cd ai-agents-with-python` / `python -m venv .venv` | ✓ Python 3 stdlib (`python -m venv`) |
| ch-02.md:35 | bash | `.venv\Scripts\activate` | ✓ Windows activation |
| ch-02.md:41 | bash | `source .venv/bin/activate` | ✓ macOS/Linux activation |
| ch-02.md:53 | bash | `python -m pip install "smolagents==1.26.0" jupyterlab python-dotenv` | ✓ pip with version pin on `smolagents`, unpinned `jupyterlab` and `python-dotenv` (consistent with style-guide age-risk table for unpinned third-party packages) |
| ch-02.md:73 | dotenv | `.env.example` template with `HF_TOKEN=`, `OPENAI_API_KEY=`, `ANTHROPIC_API_KEY=` placeholders + comment | ✓ Literal template, no real secrets |
| ch-02.md:86 | gitignore | Canonical Python entries: `.venv/`, `venv/`, `env/`, `.env`, `__pycache__/`, `*.py[cod]`, `*$py.class`, `*.egg-info/`, `build/`, `dist/`, `.ipynb_checkpoints/` | ✓ All canonical Python entries the chapter references (virtual env, secrets, bytecode, distribution, Jupyter checkpoints) |
| ch-02.md:115 | bash | `python -c "import smolagents; print(smolagents.__version__)"` (runnable check) | ✓ The runnable check from the style-guide § "Runnable checks" rubric |

Code-block language tags follow style-guide § "Code blocks" (`python`, `bash`, `text`, `dotenv`). `gitignore` and `dotenv` are extensions beyond the style-guide's named-tag list but are conventional and read correctly in any markdown viewer.

### 8. Forward-pointer hygiene — VERDICT PASS_WITH_WARN

- ch-02.md:129 "What's next" paragraph: present, two sentences, names ch-03 explicitly, mentions the `.venv` installed in this chapter. Matches style-guide § "Reading aids" exactly.
- "What's next" content: "in ch-03, you write your first short Python program — values, variables, `print()`, `input()`, and the four beginner error categories — running it in the `.venv` you built. By the end of it, you've saved, run, and slightly modified a real script." — names 4 of 5 ch-03 outcome-line elements (the 5th, f-strings, is implicit). ✓
- Length: 2 sentences, well within the one-or-two-sentence cap. ✓
- WARN (also surfaced in § 5): three body-prose forward-pointers beyond "What's next" — see § 5 above for details.

### 9. Outcome-line contract — VERDICT PASS

Outline ch-02 outcome line (outline.md:251): "Working Python 3.10+ `.venv` with smolagents and JupyterLab, `.gitignore`, `.env.example`."

Style-guide outcome action (style-guide.md:68): "Reader runs the four cross-platform install steps in the book's `.venv` and confirms `python -c "import smolagents; print(smolagents.__version__)"` prints `1.26.0`."

Chapter outcome-line callout (ch-02.md:127): "**The move:** Run the four cross-platform install steps above in the book's `.venv`, then run the version check to confirm `python -c "import smolagents; print(smolagents.__version__)"` prints `1.26.0`."

Verbatim match with the style-guide's reader-facing action. The chapter closes with this imperative; no "in this chapter we explored..." closing. ✓

### 10. No regression vs. dev re-review — VERDICT PASS

- Fix-loop "What's next" paragraph at ch-02.md:129: preserved verbatim from the dev-fix1 verdict.
- Opening orientation at ch-02.md:3: preserved verbatim (matches the dev re-review's reported line).
- Outcome line at ch-02.md:127: preserved verbatim.
- Three LOWs from the original dev review remain correctly judged as "no change required":
  - LOW 1 (`python -c "..."` in the runnable check vs. the chapter's `python -m` framing): still at ch-02.md:115-117, unchanged. The chapter's three-mode framing at lines 59-63 legitimizes `python -c` as a documented third option.
  - LOW 2 (production-wins-over-`.env` rule described behaviorally, not named): still at ch-02.md:67, unchanged.
  - LOW 3 (restatement says "ch-07 onward," outline says "ch-08 onward"): still present at ch-02.md:3 and ch-02.md:139, unchanged. **Master's lane:** the typo lives in the outline, not the chapter.
- Prose word count (after re-extraction): 1388 words. Dev re-review reported 1411. Difference is counting-method (regex `[A-Za-z][A-Za-z']*` vs. `wc -w` style); both within the ±10% band [1266, 1548] for the 1407 baseline.
- No new forbidden vocabulary introduced.
- No framework-name leaks: `HfApiModel` 0, `ApiModel` 0, `CodeAgent` 0, `final_answer` 0, `@tool` 0 occurrences.

## Cross-cutting findings

1. **Forward-pointer hygiene (cross-checked in § 5 and § 8):** Three body-prose forward-pointers at ch-02.md:63, 80, 80. Specific named-chapter references, not vague hand-waving. Reader-comprehension-valuable but technically outside the style-guide § "Reading aids" rule. Recommend master decide.

2. **Opening/closing phrasing consistency (LOW):** Line 3 reads "Python 3.10 or newer" while line 139 reads "Python 3.10+." Same meaning, different phrasing. Either change line 3 to "Python 3.10+" (conciseness) or line 139 to "Python 3.10 or newer" (verbose-but-grammar-correct). Borderline — readers will not notice; copy-editor would.

3. **Line 9 dense sentence (LOW):** "The smolagents PyPI project page lists 'Requires: Python >=3.10' on its metadata, and the Python Software Foundation's 'Active Python releases' page lists 3.10, 3.11, 3.12, 3.13, and 3.14 as the actively supported versions." 41 words, joined by "and." Two independent facts (smolagents' floor + the PSF's active-version list). Could split for breathing room but works as-is. Style-guide allows longer sentences for explanation; this is explanation.

4. **"stays reproducible" phrasing at ch-02.md:11 (LOW):** "'Reinstall later' stays reproducible when the chapter and your interpreter match." Terse — the reader must parse what "stays" refers to (the option to reinstall, the env itself, or the reproducibility). Slight ambiguity. Could be "Reinstalling later stays reproducible..." for clarity. Minor.

5. **Age-risk list at ch-02.md:9 (LOW):** "lists 3.10, 3.11, 3.12, 3.13, and 3.14 as the actively supported versions" — this list ages the moment 3.15 lands. The chapter flags age-risk for the Windows section at line 15 but not for the Python version list itself. Style-guide § "25 inline age-risks" recommends directional phrasing for version-specific facts; the floor ("Python 3.10 or newer") is fine but the specific version list could be flagged with a parenthetical "(at time of writing, August 2026)." Minor.

## Out-of-scope observations

- **Outline typo:** ch-02 outcome line in outline.md:251 says "ch-08 onward will need" but the chapter (correctly) says "ch-07 onward will need" at ch-02.md:3 and ch-02.md:139. The chapter is internally consistent. The outline typo is master's lane per the dev-fix1 review. **Not blocking** — the chapter is correct as written.
- **`HfApiModel` / `ApiModel` placement:** The chapter mentions `InferenceClientModel` once at ch-02.md:80 (as a forward-pointer for ch-09). It does not mention `HfApiModel` (correct — that class name is restricted to ch-09's one-time sidebar per style-guide § "Pinning rules"). No leak. ✓
- **Self-critique HTML comment at ch-02.md:131-137:** the book-writer skill's self-critique is preserved as an HTML comment. Per the `book-gen mode` notes in `AGENTS.md`, this comment is intended for orchestrator/reviewer handoff and should be stripped before external publish. The comment does not affect the rendered chapter. **Reminder only — master's lane.**
- **Run-on orientation paragraph at ch-02.md:3:** 43-word sentence enumerating 4 deliverables. Verbatim from the style-guide's outcome-line template. Acceptable as the chapter's contract line.

## Honest assessment

The chapter is line-edit clean. Voice, vocabulary, pacing, terminology, citations, cross-platform accuracy, code conventions, forward-pointer discipline (modulo 3 specific WARNs), outcome-line contract, and dev-fix1 regression checks all pass. The 4 WARNs surfaced are real but minor — none would survive a fix loop's cost-benefit analysis. The chapter is ready to ship to Phase 7 copy-edit (or directly to publishing if Phase 7's copy-edit pass is skipped on partial runs per `book-gen mode`).

The chapter's biggest strength: it never drops the reader's hand. Every claim is sourced, every command is runnable, every cross-platform fork is named. The biggest stylistic risk is the body-prose forward-pointers — they are useful for the reader but technically against the style-guide's reading-aids rule. Master's call.

I rate this chapter ready for line-edit sign-off. I do not recommend a fix loop. If master wants the 3 forward-pointers tightened, that is a one-line edit per reference (replace "(ch-17, ch-18, ch-19)" with "later project chapters", etc.) and can be batched into the next chapter's normal maintenance pass.

## Self-critique

- **What I checked thoroughly:** blacklist scan (10 forbidden terms, 0 matches); contraction use (verified visually); named-source citation count (15+ inline citations mapped to claims); code-block language tags (all 7 blocks tagged correctly); forward-pointer hygiene (all `ch-NN` references mapped); outcome-line verbatim match (style-guide vs. chapter callout).
- **What I might have under-checked:** I did not run `python -m venv .venv` in a clean directory to re-verify the install commands work on a fresh machine. The dev-fix1 review already verified the runnable check at lines 115-117 prints `1.26.0`. I trust that finding.
- **What I might have over-flagged:** § 5 + § 8 surface the same 3 forward-pointers twice. I considered de-duplicating but kept both because § 5 frames them as a citation-hygiene rule and § 8 frames them as a reading-aids rule — different angles, same data.
- **What I might have missed:** I did not cross-reference each subheading against the style-guide's subheading taxonomy. Subheadings are sentence-fragment style and describe the move (not the topic), per style-guide § "Subheadings." All 8 subheadings follow this pattern. ✓
- **PONTAIL note:** The style guide prescribes a tight voice for a technical-onboarding book. I did not propose any "richer" or "more expressive" prose alternatives because that would violate the style-guide's "Conversational technical" register. The chapter is as boring as it needs to be — that's the register. No action.

## Sign-off

ch-02 line-edit verdict: **PASS_WITH_WARN.**

- 0 FAIL.
- 4 WARN (3 forward-pointer hygiene, 1 phrasing consistency / 2 LOW stylistic notes).
- No fix-loop recommended.
- No regression vs. dev-fix1.
- Ready to advance to Phase 7 copy-edit (or to publish if Phase 7 is skipped per the chapter-gen structural-change plan).

Ledger ch-02 row should move: dev-reviewed → line-edited.

max_fix_loops = 3 (not used this pass).
