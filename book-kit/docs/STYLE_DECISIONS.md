# Style decisions -- visual-style samples

Four presentation choices come up in almost every book the kit produces, and
they are hard to settle in the abstract: dialogue density, tashkeel level,
scene-break style, and closing-hook length. `book-kit/examples/` holds ten
rendered samples, one per option, so the choice can be made by looking at
prose rather than by arguing about it.

Each sample ships as a matched pair: a `.html` source and the `.pdf` Chrome
rendered from it. Read the PDF to judge the typography, read the HTML to copy
the markup.

**Within each group the prose is held constant and only the style dimension
changes.** The three tashkeel samples are the same 430 words at three
vocalisation levels; the three separator samples are the same three scenes
with three different breaks. Diffing two samples in a group therefore shows
the style choice and nothing else.

## How to use this document

1. Open the two or three samples in the group you are deciding.
2. Read the "Use when" and "Avoid when" rules below.
3. Record the decision in the book's `style-guide.md` under `## Presentation`.
4. Where the kit mechanically enforces the choice, wire the matching config
   (noted per group below) so `book_check.py` and `check_chapter.py` agree
   with the guide.

---

## Group 1 -- dialogue density

| Sample | Words | Rendered pages |
|---|---:|---:|
| `dialogue-dense.html` / `.pdf` | 478 | 4 |
| `dialogue-sparse.html` / `.pdf` | 489 | 2 |

Both samples render the same rooftop scene between the same two characters.

### `dialogue-dense`

Dialogue carries the scene; narration is reduced to stage direction. Roughly
three of every four paragraphs are a single spoken line.

- **Use when:** confrontation and interrogation beats, character-vs-character
  chapters, and any scene whose meaning is produced by what people say to
  each other. Also the right default for a book that will be adapted or read
  aloud.
- **Avoid when:** the chapter's subject is interiority. Dense dialogue cannot
  show a character not saying something, which is often the whole point.
- **Cost:** the same word count occupies twice the pages (4 vs 2 here),
  because each spoken line takes a paragraph of its own. Budget for it in
  `## Word-count windows`.

### `dialogue-sparse`

Narration carries the scene; dialogue is rationed to a few load-bearing lines
that land harder because they are rare.

- **Use when:** interior chapters, memory and grief passages, and scenes
  where the point is what a character does not say.
- **Avoid when:** the chapter has three or more speakers. Sparse dialogue
  makes attribution hard to follow without falling back on speaker tags.

### What the kit enforces

Both samples use Arabic guillemets (`U+00AB` / `U+00BB`) for speech, which is
what the kit's checks expect:

- `check_chapter.py` `quote_pair_balance` -- guillemets must balance across
  the chapter and within each paragraph.
- `check_chapter.py` `dialogue_own_line` -- a paragraph containing speech
  must not also carry narration. Both samples satisfy this; it is the reason
  the dense sample runs to four pages.

---

## Group 2 -- tashkeel level

All three samples are the same 430-word passage. The ratio column is the
metric `book_check.py` computes: Unicode `Mn` (combining mark) characters
divided by total Arabic-range characters.

| Sample | Measured tashkeel ratio | Rendered pages |
|---|---:|---:|
| `tashkeel-full.html` / `.pdf` | 0.452 | 2 |
| `tashkeel-minimal.html` / `.pdf` | 0.026 | 1 |
| `tashkeel-none.html` / `.pdf` | 0.000 | 2 |

### `tashkeel-full` (ratio ~0.45)

Full vocalisation: harakat on effectively every word.

- **Use when:** children's books, poetry, Quranic or classical quotation,
  teaching texts, and any book whose reader cannot be assumed to disambiguate
  from context.
- **Avoid when:** the book is modern adult prose. Full vocalisation reads as
  didactic and slows a fluent reader down.
- **Cost:** the highest of the three. Full tashkeel is slow to author, easy
  to get subtly wrong, and expensive to proofread, because an incorrect
  haraka is a real error that a fluent reader will notice.

### `tashkeel-minimal` (ratio ~0.03)

Selective vocalisation: harakat only where a word would otherwise be
ambiguous, plus shadda where it changes meaning.

- **Use when:** general adult fiction and non-fiction. **This is the default
  for most books** and the level to pick when the decision is not obvious.
- **Avoid when:** the book teaches the language itself rather than using it.

### `tashkeel-none` (ratio 0.000)

No vocalisation at all.

- **Use when:** journalism, technical and business prose, and translated
  non-fiction where the vocabulary is modern and the reader is fluent.
- **Avoid when:** the text carries proper nouns, rare words, or verse whose
  reading a fluent reader could still get wrong.

### What the kit enforces

`book_check.py` reads per-chapter targets from the book's
`tashkeel-policy.md` under `## Per-chapter targets` (chapter, target,
tolerance) and fails the chapter when the measured ratio drifts outside the
tolerance. Set the target from the sample matching the chosen level: use
about `0.45` for full, about `0.03` for minimal, and `0.0` for none, and pick
a tolerance wide enough to survive normal prose variation. Chapters absent
from that table are not ratio-checked at all.

---

## Group 3 -- scene-break separator

All three samples are the same three scenes with three different break
treatments.

| Sample | Break marker | Rendered pages |
|---|---|---:|
| `separator-asterism.html` / `.pdf` | asterism, `U+2042` | 2 |
| `separator-blank.html` / `.pdf` | vertical whitespace only | 2 |
| `separator-ornament.html` / `.pdf` | rub el hizb, `U+06DE` | 2 |

### `separator-asterism`

A centred asterism between scenes.

- **Use when:** literary fiction with frequent scene changes, where the
  reader needs an unambiguous visual stop that survives reflow and page
  breaks.
- **Avoid when:** the book's visual identity is explicitly Arabic; the
  asterism reads as a Western typographic convention.

### `separator-blank`

Vertical whitespace only, with no printed glyph.

- **Use when:** quiet, continuous narration where a printed mark would feel
  intrusive, and in books with few scene changes per chapter.
- **Avoid when:** the book will be paginated tightly. **This is the one
  option with a correctness risk:** when the gap falls at a page boundary it
  disappears entirely, and the reader runs two scenes together. Pick a glyph
  separator if the book is long, dense, or destined for a small trim size.

### `separator-ornament`

A centred Arabic ornament (rub el hizb) between scenes.

- **Use when:** books with an explicitly Arabic or classical visual identity,
  and gift or heritage editions where the ornament is part of the design
  language.
- **Avoid when:** the book is plain contemporary prose, or the production
  font may lack the glyph. Verify the ornament renders in the chosen font
  before committing to it -- an absent glyph shows as a tofu box, and the
  sample here is set at 26pt precisely because the glyph renders lighter
  than the asterism at the same nominal size.

### What the kit enforces

Nothing mechanical. Separator style is a pure presentation choice; record it
in `style-guide.md` under `## Presentation` -> structural devices. If a
consistent marker is wanted, add the wrong ones to `## Forbidden patterns` so
`book_check.py` catches a drifting separator.

---

## Group 4 -- closing-hook length

Both samples are the same chapter ending with a different final paragraph.

| Sample | Closing-hook words | `closing_hook` result |
|---|---:|---|
| `closing-hook-short.html` / `.pdf` | 7 | PASS |
| `closing-hook-long.html` / `.pdf` | 67 | FAIL |

Both results are measured by running the kit's own
`check_chapter.py closing_hook` against the sample's final paragraph.

### `closing-hook-short` (7 words)

The chapter ends on a compressed hook.

- **Use when:** serialised and commercial fiction where each chapter must
  pull the reader into the next; thrillers; any book read in short sittings.
- **Avoid when:** the chapter has earned a reflective landing and the short
  hook would feel like a gimmick.
- Satisfies the kit's default rule (see below) with no configuration.

### `closing-hook-long` (67 words)

The chapter ends on an extended reflective sentence.

- **Use when:** non-fiction and literary fiction that closes on interiority
  rather than momentum, and in a final chapter, where a hook into a
  non-existent next chapter would be false.
- **Avoid when:** the book depends on chapter-to-chapter pull.
- **This sample deliberately fails the kit's default check.** It is included
  because a legitimate book-level choice should not look like a bug when the
  checker reports it.

### What the kit enforces

`check_chapter.py` `closing_hook` reads the last paragraph before the
`<!-- end-of-chapter -->` marker (or the last paragraph of the file when the
marker is absent) and fails when it exceeds `max_words`, default `8`. A book
that chooses long hooks should raise that ceiling in its style guide and
dispatch rather than absorb a standing FAIL on every chapter.

---

## Rendering and regeneration

The committed PDFs were produced from the committed HTML by
`book-kit/bin/render-examples.sh`, which drives Chrome headless with the same
flags `md2pdf.py` uses (`--headless=new --disable-gpu --no-sandbox
--no-pdf-header-footer --print-to-pdf`). The sample CSS mirrors `md2pdf.py`'s
`DEFAULT_CSS`: A4, RTL body flow, the Cairo font stack, and the same heading
palette, so a sample looks like a page of a real book-kit build rather than a
generic browser page.

Re-render after editing any sample:

```sh
bash book-kit/bin/render-examples.sh --dry-run   # list the 10 pairs
bash book-kit/bin/render-examples.sh             # render them
```

Set `CHROME_PATH` if Chrome is installed somewhere non-standard; the script
exits 2 when it cannot find a browser. It exits 3 when a render produced a
missing or implausibly small PDF, which is the signal that Chrome failed to
load the input and printed its own error page instead -- a failure mode that
otherwise exits 0 and ships a broken sample.

### Fidelity notes

- Page counts depend on the fonts installed on the rendering machine. The
  counts in this document come from the committed PDFs and are indicative,
  not guaranteed.
- The English banner at the top of each sample identifies the sample and its
  rule. It is not part of the demonstrated style and would not appear in a
  real chapter.
- Samples are synthetic prose written for this directory. They are not drawn
  from any book in `books/`.
