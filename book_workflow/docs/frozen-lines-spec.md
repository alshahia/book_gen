# Frozen-Lines Spec

> Canonical reference for the frozen-line manifest protocol in book-gen. Read by master (Phase 4 close) and by am-coder (Phase 6 mechanical gate).

## What problem this solves

In a multi-chapter book, certain lines carry structural weight: opening lines, anchor metaphors, character-defining phrases. These are the lines that, if changed, break inter-chapter payoffs and reader continuity. Without enforcement, a writer (am-coder) might unconsciously rephrase a frozen line during a flow state; the line-edit review might catch it days later when the payoff chapter is already drafted.

Frozen-lines.json moves the constraint from prose-memory to mechanical gate.

## Schema

`books/<slug>/frozen-lines.json` — see `book_workflow/book-agents/templates/frozen-lines.schema.json` for the JSON Schema. Required fields:

| Field | Type | Purpose |
|---|---|---|
| `version` | const 1 | Schema version. |
| `chapters` | object | Keyed by `ch-NN.md`. |
| `chapters.<file>.frozen_lines` | array | Each entry is one immutable line. |
| `chapters.<file>.frozen_lines[].line_number` | integer >= 1 | 1-indexed line in the chapter file. |
| `chapters.<file>.frozen_lines[].sha256` | string (hex 64) | SHA256 of the line bytes (incl. trailing newline). |
| `chapters.<file>.frozen_lines[].source` | string | style-guide.md section reference, e.g. `style-guide.md §Frozen lines > ch-05 > «لأول مرة...»`. |
| `chapters.<file>.frozen_lines[].why` | string | Human-readable rationale — forces a reason. |

## Lifecycle

| Phase | Owner | Action |
|---|---|---|
| Phase 4 close (style-guide confirmation) | master (after am-design writes style-guide.md) | Reads `## Frozen lines` section from style-guide.md. For each `(chapter, line)` declaration, computes SHA256 of the (currently empty or stub) chapter file or records a sentinel hash. Writes `books/<slug>/frozen-lines.json`. |
| Phase 6 (per-chapter writing) | am-coder via book-writer skill + `book_check.py` | Before marking `drafted`, runs `python3 book_workflow/scripts/book_check.py books/<slug>/`. The script computes SHA256 of each declared line in the live chapter file, compares against the manifest. Mismatch -> exit 1 with `ch-NN:line_number` evidence. |
| Phase 6 (amendment request) | am-coder -> master -> user | If am-coder judges a frozen line must change, am-coder STOPS. Surfaces to master. Master checks: is this a real need (e.g., later outline revealed the line contradicts an established fact)? If yes, master surfaces to user at next checkpoint. User confirms -> style-guide amended -> manifest regenerated -> am-coder proceeds. |
| Phase 7 (line-edit review) | am-review + `book_check.py` | Re-runs T1 as part of line-edit pass. Verifies manifest byte-equality. Any drift = FAIL. |
| Phase 5b (export) | `build_exports.py` | Archives `frozen-lines.json` to `books/<slug>/exports/manifest.json` for the record. |

## Why SHA256 not raw text

- Immune to trailing-whitespace / CRLF drift on Windows working tree.
- Compresses the manifest: even a 5,000-line chapter with 30 frozen lines produces a 30-entry manifest of ~150 bytes each.
- Verifiable in O(1) per line; the script reads the file once into memory and hashes only the declared line slices.

## Why the `why` field

Forces am-design / master to articulate the rationale. If the only answer is "I just want this frozen", the line probably does not need to be frozen. Catches the over-freeze failure mode (every line marked frozen -> nothing frozen means anything).

## Example

For a fictional Arabic book where the first line of ch-05 carries the chapter's emotional anchor:

```json
{
  "version": 1,
  "chapters": {
    "ch-05.md": {
      "frozen_lines": [
        {
          "line_number": 47,
          "sha256": "8a3f0d2e1c9b8a7f6e5d4c3b2a1908f7e6d5c4b3a2918071605142310987654",
          "source": "style-guide.md §Frozen lines > ch-05 > «لأول مرة...»",
          "why": "Opening line carries the chapter's emotional anchor; any rewording breaks the interlink payoff with ch-02."
        }
      ]
    }
  }
}
```

## Failure modes

| Failure | Detection | Handling |
|---|---|---|
| Manifest missing | `book_check.py` reads `frozen-lines.json`, gets FileNotFoundError | Exit 1 with "manifest not found, regenerate at Phase 4 close" |
| Chapter file missing | Manifest references `ch-05.md` but file does not exist | Allowed during Phases 1-5 (chapters not yet written). `book_check.py` skips. |
| SHA256 mismatch | Computed hash != manifest hash | Exit 1 with chapter:line. am-coder MUST fix or surface. |
| User requests frozen-line change | Style-guide amendment + manifest regeneration required | Master writes new manifest before am-coder resumes. |
| Manifest drift across regenerations | Each regeneration recomputes from style-guide, so drift is impossible by construction | - |

## Open questions

- Should frozen lines survive across book editions (v2 of the same book)? -> spec'd as no. Manifest is per-book-slug.
- Can a frozen line reference a line that does not exist yet? -> yes, sentinel hash recorded; first writer dispatch must hash the actual line.
