---
scope: role
topic: Windows/WSL bash gotchas in context_gen repo
status: active
superseded_by:
created: 2026-07-04
last_verified: 2026-07-04
---

## TL;DR

On this Windows repo the pwsh→WSL bash bridge mangles multi-line/loop/`$()` inline commands — write test scripts to a file and run them instead.

## Context

Dispatched to write `scripts/backfill-research-metrics.sh`. Multiple `bash -c 'for f in ...; do ...; done'` and inline `$(...)` one-liners silently corrupted (loop var came back empty, exit codes misread as 0). Cost several wasted tool calls.

## Insight

- Inline `bash -c '...'` with `for` loops, `$n` in loops, or nested `$(...)` gets corrupted through the pwsh shell. Fix: write the test/helper to a `.sh` file (temp dir is fine), `sed -i 's/\r$//'` it, then `bash file.sh`. Single simple commands are OK inline.
- Repo has `core.filemode=false`; scripts are tracked `100644` and invoked via `bash scripts/x.sh` — `chmod +x` won't persist a distinct git mode, and the `-rwxr-xr-x` ideal isn't achievable. Don't rely on the exec bit.
- Working-tree `.md`/`.sh` files may be CRLF even though `.gitattributes` normalizes to LF on commit. When appending to a file, detect and match its EOL; always `sed -i 's/\r$//'` new `.sh` files or the shebang breaks.
- WSL path for `E:\context_gen` is `/mnt/e/context_gen`.

## Source

`share/notes/03_coder_summary_T-2026-07-04-004_P3D2.md`

## Verification

Re-run any `bash -c 'for x in a b; do echo $x; done'` through the shell tool — the loop body prints empty. Contrast with a `.sh` file which runs correctly. `git config core.filemode` → `false`; `git ls-files -s scripts/validate-memory.sh` → `100644`.
