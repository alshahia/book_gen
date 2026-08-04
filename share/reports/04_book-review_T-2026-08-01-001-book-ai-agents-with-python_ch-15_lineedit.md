# Book Review Report — T-2026-08-01-001-book-ai-agents-with-python / ch-15 line edit

**Date:** 2026-08-03
**Sub-agent:** am-review
**Pass:** line edit, post dev-fix1

## Summary

- **Overall verdict:** FAIL
- **Checklist:** 11 PASS / 5 FAIL / 2 N/A
- **Issues:** 0 CRITICAL / 4 HIGH / 1 MEDIUM / 0 LOW
- **Block acceptance?** yes

The chapter is technically sound and its voice is mostly controlled, but it does not meet the explicit line-edit contract: the closing callout exceeds 80 words, the final bridge omits ch-17, required acronyms are not expanded on first use, and the ledger still records the old draft state.

## Tests / build run

- Blacklist scan, case-insensitive word boundaries, whole chapter including comments and code — **PASS**, 0 hits.
- Chapter scan for `HfApiModel` and `ApiModel` — **PASS**, 0 hits at `books/ai-agents-with-python/chapters/ch-15.md:1-208`. A repository-wide scan is not a meaningful zero test because governance/reference files intentionally discuss these names; the chapter itself satisfies the chapter contract.
- Exact-word scan for `\bfinal_answer\b`, whole chapter including code and HTML comment — **PASS**, 0 hits. `final_answer_checks` does not match the exact-word expression.
- Python fence extraction + `ast.parse` under `E:\book_gen\.venv\Scripts\python.exe` — **PASS**, 3/3 blocks parse.
- Runtime execution of the second Python block under the book venv — **PASS**; generated `final_answer('Visit https://example.org for details')`, terminated on step 1, and printed `Visit https://example.org for details | success` (`ch-15.md:73-107`).
- UTF-8 encode/decode round trip — **PASS**.
- Paragraph scan — **FAIL**; the closing callout is 82 lexical words at `ch-15.md:171`, above the required 80-word ceiling.
- Orientation count — **PASS**, 59 words at `ch-15.md:3`.
- Word-count range — **PASS** using the supplied post-fix1 count of 1,676; allowed range is 1,508–1,844. The ledger has not been updated to that count (`ledger.md:41`).

## Required checklist

1. **PASS — Vocabulary blacklist.** Zero case-insensitive, word-boundary hits in prose, code comments, docstrings, or the HTML self-critique (`ch-15.md:1-208`).
2. **PASS — Person and passive voice.** Direct second person appears throughout (`ch-15.md:3`, `ch-15.md:21`, `ch-15.md:63`, `ch-15.md:171`). Technical passive constructions such as “verified” and “generated” describe source verification or code provenance rather than replacing reader-facing instruction (`ch-15.md:61`, `ch-15.md:69`, `ch-15.md:171`).
3. **PASS — Contractions and punctuation.** Natural contractions appear (`ch-15.md:9`, `ch-15.md:63`); no exclamation marks occur.
4. **FAIL — Pacing and paragraph length.** Most paragraphs carry one move, but the final callout bundles classification, imports, executor isolation, step limits, answer checks, secret storage, ignore rules, and redaction into 82 words (`ch-15.md:171`). This exceeds the absolute 80-word limit.
5. **PASS — Subheading style.** The ten H2 headings are action-oriented fragments and no heading exceeds seven words (`ch-15.md:5`, `ch-15.md:13`, `ch-15.md:19`, `ch-15.md:33`, `ch-15.md:57`, `ch-15.md:65`, `ch-15.md:111`, `ch-15.md:119`, `ch-15.md:153`, `ch-15.md:163`).
6. **PASS — Named sourcing.** Non-obvious security claims name OWASP, Anthropic, NIST, or the installed smolagents 1.26.0 source (`ch-15.md:7`, `ch-15.md:11`, `ch-15.md:35`, `ch-15.md:55`, `ch-15.md:59-69`, `ch-15.md:113`, `ch-15.md:121`).
7. **PASS — Model-name prohibition.** Zero chapter mentions of `HfApiModel` or `ApiModel`.
8. **PASS — Exact terminator token prohibition.** Zero `\bfinal_answer\b` matches in the complete file. The runtime construction at `ch-15.md:86-89` avoids the literal token.
9. **FAIL — Acronyms on first use.** OWASP and NIST are introduced without expanding their organization names (`ch-15.md:7`, `ch-15.md:11`). “API” appears without “application programming interface” (`ch-15.md:167`), and “JSON”/“JSONL” appears without expansion (`ch-15.md:148`, `ch-15.md:171`). AST, ML, and OS do not appear as standalone visible chapter acronyms, so those three are N/A rather than failures.
10. **PASS — Orientation.** The 59-word opening starts with a concrete URL/agent/terminal scene and presents the problem rather than summarizing the chapter (`ch-15.md:3`; style guide `style-guide.md:36`).
11. **FAIL — Forward pointer.** The ending names ch-16 but does not name ch-17 or its full title, *Choose and Operate Model Backends* (`ch-15.md:173`). Ch-17 appears earlier with its full title (`ch-15.md:167`), but the checklist explicitly requires it in the final “What's next” pointer.
12. **PASS — Closing placement.** `> **The move:**` is the final visible substantive prose paragraph, followed only by the permitted thin “What's next” bridge and the HTML comment (`ch-15.md:171-175`).
13. **PASS — No recap after imperative.** The bridge is a dependency pointer, not an authorial summary or third-person outcome line (`ch-15.md:173`).
14. **PASS — Word count.** Supplied count 1,676 is within tolerance.
15. **PASS — UTF-8.** Fresh round-trip check succeeded.
16. **PASS — Code regression.** All three blocks parse; the runtime-built terminator executes and ends the agent successfully (`ch-15.md:39-53`, `ch-15.md:73-107`, `ch-15.md:123-149`).
17. **N/A — Earlier bible blocks untouched.** The workspace is not a Git repository, so there is no baseline diff or hash with which to prove that ch-01..ch-14 blocks are unchanged. Current ch-14 and ch-15 boundaries remain present at `bible.md:164` and `bible.md:172`.
18. **FAIL — Ledger update.** The ch-15 row still says `drafted`, records 1,532 words, and leaves review fields as `-` (`ledger.md:41`). It does not reflect the supplied 1,676-word post-fix1 line-edit state.

## Issues

- **[HIGH]** `chapters/ch-15.md:171` contains an 82-word visible prose paragraph; split or tighten it to 80 words or fewer.
- **[HIGH]** `chapters/ch-15.md:173` omits the required ch-17 pointer and full title. Add “ch-17 — Choose and Operate Model Backends” naturally to the bridge.
- **[HIGH]** `chapters/ch-15.md:7`, `:11`, `:148`, and `:167` introduce required acronyms without expansion. Expand Open Worldwide Application Security Project (OWASP), National Institute of Standards and Technology (NIST), JavaScript Object Notation (JSON), and application programming interface (API) at first visible use.
- **[HIGH]** `books/ai-agents-with-python/ledger.md:41` remains stale (`drafted`, 1,532, no review verdicts). Update it through the proper writer/master lane after chapter fixes.
- **[MEDIUM]** `chapters/ch-15.md:86-89` explains why the terminator is assembled, but a beginner still has to infer that the framework expects the resulting call name. Add one short sentence after the block explaining that concatenation produces the framework's terminator at runtime solely to satisfy the whole-file grep contract.

## Cross-cutting findings

- The technical safety sequence is coherent: classify effects, constrain imports, isolate untrusted code, cap the loop, validate output, and redact persistence boundaries (`ch-15.md:19-171`).
- The four beginner errors match the established error-section shape: each is named in a short lead sentence and immediately corrected with a concrete boundary (`ch-15.md:153-161`).
- The ch-17 sentence at `ch-15.md:167` flows naturally from blast radius to backend choice. The defect is placement: the required ending bridge at `ch-15.md:173` mentions only ch-16.

## Out-of-scope observations

- Repository-wide occurrences of `HfApiModel`/`ApiModel` exist in style and governance material by design. The enforced chapter scan is clean; treating those reference files as chapter prose would create a false failure.

## Honest assessment

The chapter reads cleanly and the code remains executable. The runtime terminator construction is not unexplained magic—the comment states the grep reason—but it is still mildly awkward pedagogy because it optimizes the example around an editorial scan rather than the reader's mental model; one plain sentence after the block would resolve that. The four beginner errors are well formed and consistent with the earlier pattern. No blacklist words are hidden in comments, docstrings, or the HTML self-critique, but the 82-word closing callout is a real paragraph-length violation.

## Self-critique

- **Did I do my job?** Yes: I read the complete chapter and style guide, ran fresh scans, parsed all code blocks, and executed the terminator block.
- **What might I have missed?** I did not rerun the first and third blocks end-to-end because the dispatch specifically identified the terminator regression and stated all three were previously verified; I did independently parse all three.
- **What did I assume without evidence?** The exact 1,676 prose count comes from the dispatch context. I could verify it is plausible and in range, but prose-count definitions vary around code, headings, and callouts.
- **Baseline limitation:** Without Git history or a supplied pre-fix hash, I cannot prove the earlier bible blocks are byte-for-byte untouched.
