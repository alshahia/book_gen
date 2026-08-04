#!/usr/bin/env python3
"""Validate YAML frontmatter in SKILL.md files.

Stdlib-only. Checks:
  - file starts with `---` on line 1
  - frontmatter block ends with `---`
  - required fields: `name`, `description`
  - `name` matches regex `^[a-z0-9]+(-[a-z0-9]+)*$`
  - `name` matches parent directory name
  - `description` length is 1..1024 chars

Usage:
    python3 scripts/validate-frontmatter.py path/to/SKILL.md [more ...]
"""
import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def parse_frontmatter(path):
    """Return (frontmatter_dict, body) or raise ValueError."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ValueError(f"{path}: must start with `---` on line 1")

    # Find closing `---`
    end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == "---":
            end = i
            break
    if end is None:
        raise ValueError(f"{path}: frontmatter not closed with `---`")

    fm = {}
    for raw in lines[1:end]:
        line = raw.rstrip("\r\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1).lower()
        val = m.group(2).strip()
        # Strip surrounding quotes if present
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        fm[key] = val

    return fm, "".join(lines[end + 1 :])


def is_skill_path(path):
    """Strict validation only applies to OpenCode-discoverable skills.

    OpenCode's loader searches paths containing a `skills/` segment.
    Files outside that path (e.g. internal references loaded via `read`
    tool by agents) are agent-managed, not skill-loader-managed, so
    the strict name regex + dir-match rule does not apply.
    """
    abspath = os.path.abspath(path)
    return f"{os.sep}skills{os.sep}" in abspath


def validate_one(path):
    errors = []
    try:
        fm, _ = parse_frontmatter(path)
    except ValueError as e:
        return [str(e)]

    name = fm.get("name", "").strip()
    desc = fm.get("description", "").strip()
    strict = is_skill_path(path)

    if not name:
        if strict:
            errors.append(f"{path}: missing required field `name`")
    else:
        if strict:
            if not NAME_RE.match(name):
                errors.append(
                    f"{path}: `name` '{name}' does not match regex ^[a-z0-9]+(-[a-z0-9]+)*$"
                )
            else:
                parent_dir = os.path.basename(os.path.dirname(os.path.abspath(path)))
                if parent_dir != name:
                    errors.append(
                        f"{path}: `name` '{name}' does not match parent directory '{parent_dir}'"
                    )

    if not desc:
        errors.append(f"{path}: missing required field `description`")
    elif len(desc) < 1 or len(desc) > 1024:
        errors.append(
            f"{path}: `description` length {len(desc)} not in 1..1024"
        )

    mode = "strict" if strict else "lenient"
    return ([], mode) if not errors else (errors, mode)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2

    all_errors = []
    files_checked = 0
    for path in argv[1:]:
        if not os.path.isfile(path):
            all_errors.append(f"NOT_FOUND: {path}")
            continue
        files_checked += 1
        errs, mode = validate_one(path)
        if errs:
            all_errors.extend(errs)
        else:
            print(f"OK: {path} ({mode})")

    print(f"\nChecked {files_checked} files.")
    if all_errors:
        print(f"\nFAILED with {len(all_errors)} error(s):")
        for e in all_errors:
            print(f"  {e}")
        return 1
    print("All SKILL.md frontmatter valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
