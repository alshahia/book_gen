# books/

This is your manuscript workspace. One folder per book, named `kebab-case-slug`.

The Book Kit pipeline creates and manages these folders automatically when you
say "write a book about X" in OpenCode. You don't need to create them by hand.

After the first chapter ships, this directory will look like:

```
books/
  my-book-slug/
    intake.md              # Phase 0 — your answers to the 9-field intake
    skeleton.md            # Phase 1 — chapter list + depends_on tags
    research-log.md        # Phase 2 — research findings per chapter
    outline.md             # Phase 3 — full chapter outline
    style-guide.md         # Phase 4 — voice + presentation rules
    writing-plan.md        # Phase 5 — LINEAR | PARALLEL | MIXED dispatch order
    bible.md               # cumulative, append-only — facts, voice, characters
    ledger.md              # one row per chapter — status tracker
    decisions-log.md       # append-only — phase changes + scope decisions
    chapters/
      ch-01.md             # the prose itself
      ch-02.md
      ...
    reviews/               # (optional) review outputs mirrored from share/reports/
```

Don't edit `books/<slug>/chapters/*.md` directly once the pipeline starts —
that's am-coder's lane. If you need a structural change (add/remove/reorder a
chapter), tell master at Phase 5 or later and the writing plan will be
re-issued.