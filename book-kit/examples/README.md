# book-kit examples -- visual-style samples

Ten rendered samples covering four presentation decisions that come up in
almost every book: dialogue density, tashkeel level, scene-break style, and
closing-hook length.

Each sample is a matched pair -- a `.html` source and the `.pdf` Chrome
rendered from it. Read the PDF to judge the typography; read the HTML to copy
the markup.

| Group | Samples |
|---|---|
| Dialogue density | `dialogue-dense`, `dialogue-sparse` |
| Tashkeel level | `tashkeel-full`, `tashkeel-minimal`, `tashkeel-none` |
| Scene separator | `separator-asterism`, `separator-blank`, `separator-ornament` |
| Closing hook | `closing-hook-long`, `closing-hook-short` |

Within each group the prose is held constant and only the style dimension
changes, so diffing two samples in a group shows the choice and nothing else.

**The "when to use" rule for every sample lives in
[`../docs/STYLE_DECISIONS.md`](../docs/STYLE_DECISIONS.md).** Start there; the
files in this directory are the evidence behind it.

## Regenerating the PDFs

```sh
bash ../bin/render-examples.sh --dry-run   # list the 10 pairs
bash ../bin/render-examples.sh             # render them
```

The script drives Chrome headless with the same flags `md2pdf.py` uses. Set
`CHROME_PATH` if Chrome is installed somewhere non-standard. Re-run it after
editing any sample so the committed PDFs stay in sync with their sources.
