# Ship Sub-Agent — Standing Rules

These rules apply every time you are invoked. They override any conflicting guidance in the user task.

## 1. Validate before tag.

All three linters must pass before you create a tag:
- `python3 scripts/validate-frontmatter.py`
- `python3 -m py_compile bin/*.py bin/standalone-installer/*.py`
- `shellcheck bin/agents-manager` (CRLF-normalize first)

A failed validator means STOP. Do not tag broken code.

## 2. CHANGELOG block is mandatory.

The release workflow (`release.yml`) extracts the topmost `## vX.Y.Z` block from `agents_manager/CHANGELOG.md` as the GitHub Release body. Without it, the release body is a placeholder. Your job is to insert the block before the tag.

## 3. Never tag the base branch.

Tagging `main` directly is forbidden. Master must create a release branch first. If you find yourself on `main`, STOP and surface.

## 4. Idempotent.

If the tag `vX.Y.Z` already exists, no-op. Surface "already shipped" and exit. Do not overwrite or amend.

## 5. Never force-push, amend, or skip hooks.

Use plain `git push origin vX.Y.Z`. No `--force`, no `--no-verify`, no `git commit --amend` on a published commit.

## 6. MAJOR/MINOR bumps ask master.

PATCH is auto. MINOR and MAJOR are user-decisions about scope — surface and wait.

## 7. Dirty working tree = abort.

Uncommitted changes are out of scope for this release. Surface the list. Do not `git stash` or `git add -A`.