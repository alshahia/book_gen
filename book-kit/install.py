#!/usr/bin/env python3
"""Book Kit cross-platform installer.

Drops engine files (skills, opencode.jsonc, CLAUDE.md, scripts) into a target
project. Preserves user-owned content (books/**, tasks/**, user-created
share/**). Idempotent, dry-runnable, reversable.

Stdlib only. Run from the unzipped kit directory:
    python install.py [--target PATH] [--global|--local|--both]
                      [--check-only] [--uninstall] [--upgrade]
                      [--with-chub] [--no-doctor] [--copy-anyway]

When --target resolves to the kit root (e.g. `--target .` from inside the
unzipped kit) OR target already contains a manifest.json whose version
matches this kit, the installer runs in "install-in-place" mode: skips the
file-copy phase (kit files are already there), verifies their SHA against
the manifest, and continues with workspace dirs + marker + chub + doctor.
Pass --copy-anyway to force the original copy-onto-self behavior.

Exit codes:
    0  success / no-op / clean dry-run
    1  precondition failure (target not writable, missing manifest, etc.)
    2  user interrupt or unexpected error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = KIT_ROOT / "manifest.json"
VERSION_PATH = KIT_ROOT / "VERSION"
DOCTOR_PATH = KIT_ROOT / "scripts" / "doctor.py"

BANNER = "Book Kit installer"


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print("ERROR: manifest.json missing — re-download the kit", file=sys.stderr)
        sys.exit(1)
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _load_version() -> str:
    if not VERSION_PATH.exists():
        return "?"
    return VERSION_PATH.read_text(encoding="utf-8").strip()


def _run_doctor(target: Path) -> bool:
    if not DOCTOR_PATH.exists():
        print("WARN: scripts/doctor.py not found; skipping preflight", file=sys.stderr)
        return True
    env = dict(os.environ)
    env["BOOK_KIT_TARGET"] = str(target)
    rc = subprocess_run([sys.executable, str(DOCTOR_PATH)], env=env)
    return rc == 0


def subprocess_run(cmd, env=None):
    import subprocess
    return subprocess.run(cmd, env=env).returncode


def _resolve_target(args_target: str, *, allow_self: bool = False) -> Path:
    """Resolve and validate the install target path.

    allow_self=True permits target == KIT_ROOT (used for install-in-place).
    allow_self=False rejects it with the original safety error (used for uninstall,
    where writing onto the kit itself would be destructive).
    """
    p = Path(args_target).resolve()
    if p == KIT_ROOT and not allow_self:
        print(
            "ERROR: target resolves to the kit root; refusing to install into self",
            file=sys.stderr,
        )
        sys.exit(1)
    if KIT_ROOT.resolve() in p.resolve().parents and p != KIT_ROOT:
        print(
            "ERROR: target is inside the kit root; pick a folder outside the unzipped kit",
            file=sys.stderr,
        )
        sys.exit(1)
    return p


def _detect_install_in_place(target: Path, force_copy_anyway: bool, upgrade: bool) -> bool:
    """Decide whether to skip the file-copy phase.

    True (skip copy) when:
      - target == KIT_ROOT (kit files are already at target), OR
      - target has a manifest.json whose version matches this kit's VERSION
        (a prior install of the same kit version is already at target)

    False (run copy) when:
      - --copy-anyway was passed (explicit override), OR
      - --upgrade was passed (user wants to refresh files regardless)
      - target has no manifest.json (fresh install)
      - target has a manifest.json with a different version (cross-version upgrade)
    """
    if force_copy_anyway or upgrade:
        return False
    if target == KIT_ROOT:
        return True
    target_manifest = target / "manifest.json"
    if not target_manifest.exists():
        return False
    try:
        prior = json.loads(target_manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return prior.get("version") == _load_version()


def _verify_existing_files(target: Path, manifest: dict) -> list:
    """SHA-verify existing files against manifest. Return list of warnings.

    Used in install-in-place mode: kit files are already at target, but the
    user may have edited some. Surface mismatches as warnings, not failures.
    """
    warnings = []
    for entry in manifest["engine_files"]:
        rel = entry["path"]
        if rel == "manifest.json":
            continue  # self-referential sha, skip
        dst = target / rel
        if not dst.exists():
            warnings.append(f"missing: {rel}")
            continue
        actual = _hash(dst)
        if actual != entry["sha256"]:
            warnings.append(
                f"modified: {rel} (expected {entry['sha256'][:8]}, got {actual[:8]})"
            )
    return warnings


def _is_protected(rel: str) -> bool:
    # User-owned top-level paths: never overwrite content under these.
    parts = rel.replace("\\", "/").split("/")
    head = parts[0]
    return head in {"books", "tasks"}


def _copy_engine_file(target: Path, rel: str, expected_sha: str, mode: str) -> str:
    src = KIT_ROOT / rel
    if not src.exists():
        return f"missing source: {rel}"

    # manifest.json contains its own hash; we can't verify it against itself
    # without a fixed-point check. Skip the mismatch path for this one file.
    actual_sha = _hash(src)
    if actual_sha != expected_sha and rel != "manifest.json":
        return f"checksum mismatch for {rel} (expected {expected_sha[:8]}, got {actual_sha[:8]})"

    dst = target / rel
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        existing_sha = _hash(dst)
        if existing_sha == actual_sha:
            return "skip"
        if mode == "upgrade" and _is_protected(rel):
            # Should not happen (protected paths are not in engine_files), but guard anyway.
            bak = dst.with_suffix(dst.suffix + ".userbak")
            shutil.copy2(dst, bak)
            shutil.copy2(src, dst)
            return "preserved+overwritten"
        if mode in {"upgrade", "install"}:
            bak = dst.with_suffix(dst.suffix + f".bak.{_short_sha(actual_sha)}")
            if not bak.exists():
                shutil.copy2(dst, bak)
            shutil.copy2(src, dst)
            return f"overwritten (backup: {bak.name})"

    shutil.copy2(src, dst)
    return "wrote"


def _short_sha(sha: str) -> str:
    return sha[:8]


def _ensure_user_dirs(target: Path, user_files: list) -> None:
    for entry in user_files:
        rel = entry["path"].rstrip("/")
        (target / rel).mkdir(parents=True, exist_ok=True)


def _write_install_marker(target: Path, version: str) -> None:
    marker = target / ".book-kit-version"
    marker.write_text(
        json.dumps(
            {
                "version": version,
                "installed_at": _now_iso(),
                "kit_root_was": str(KIT_ROOT),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _print_summary(results: list, mode: str) -> None:
    counts = {"wrote": 0, "skip": 0, "overwritten": 0, "missing source": 0, "checksum mismatch": 0}
    for r in results:
        for k in counts:
            if r.startswith(k):
                counts[k] += 1
                break
    print()
    print(f"mode: {mode}")
    for k, v in counts.items():
        print(f"  {k}: {v}")


def cmd_install(args) -> int:
    manifest = _load_manifest()
    version = _load_version()
    target = _resolve_target(args.target, allow_self=True)
    install_in_place = _detect_install_in_place(
        target, args.copy_anyway, args.upgrade
    )

    print(f"{BANNER} v{version}")
    print(f"target: {target}")
    if install_in_place:
        print("[mode] install-in-place: kit files already present at target; skipping copy phase")
    print()

    if not args.no_doctor and not args.check_only:
        if not _run_doctor(target):
            print("doctor reported failures; rerun with --no-doctor to force install",
                  file=sys.stderr)
            return 1

    if args.check_only:
        print("check-only: not modifying any files")
        for entry in manifest["engine_files"]:
            src = KIT_ROOT / entry["path"]
            # manifest.json references its own sha — skip mismatch path
            if entry["path"] == "manifest.json":
                status = "OK" if src.exists() else "BAD"
            else:
                status = "OK" if src.exists() and _hash(src) == entry["sha256"] else "BAD"
            print(f"  [{status}] {entry['path']}")
        print("check-only complete.")
        return 0

    mode = "upgrade" if args.upgrade else "install"
    if args.upgrade:
        existing_marker = target / ".book-kit-version"
        if existing_marker.exists():
            try:
                prior = json.loads(existing_marker.read_text(encoding="utf-8"))
                print(f"upgrading from kit v{prior.get('version', '?')} -> v{version}")
            except (OSError, ValueError):
                print("upgrading (existing marker unreadable)")
        else:
            print(f"installing fresh (kit v{version})")

    _ensure_user_dirs(target, manifest["user_files"])

    if install_in_place:
        warnings = _verify_existing_files(target, manifest)
        if warnings:
            print("WARN: existing files differ from manifest:")
            print("      (user may have edited; rerun with --copy-anyway to overwrite)")
            for w in warnings:
                print(f"  - {w}")
            print()
        else:
            print("verify: all kit files match manifest")
        results = []
    else:
        results = []
        for entry in manifest["engine_files"]:
            results.append(_copy_engine_file(target, entry["path"], entry["sha256"], mode))
        _print_summary(results, mode)

    _write_install_marker(target, version)

    if args.with_chub:
        _try_install_chub()

    print()
    print("next steps:")
    print(f"  1. cd {target}")
    print("  2. launch OpenCode: opencode")
    print('  3. say: "write a book about <topic>"')
    print()
    print("to uninstall: python install.py --target . --uninstall")
    return 0


def cmd_uninstall(args) -> int:
    manifest = _load_manifest()
    target = _resolve_target(args.target)

    print(f"{BANNER} uninstall")
    print(f"target: {target}")

    removed = 0
    preserved = 0
    for entry in manifest["engine_files"]:
        dst = target / entry["path"]
        if dst.exists():
            dst.unlink()
            removed += 1
        else:
            preserved += 1

    marker = target / ".book-kit-version"
    if marker.exists():
        marker.unlink()
        removed += 1

    print(f"  engine files removed: {removed}")
    print(f"  user-owned content preserved (books/, tasks/, share/*)")
    print(f"  backup files (.bak.*) preserved in place; remove manually if unwanted")
    return 0


def _try_install_chub() -> None:
    import subprocess
    if shutil.which("chub"):
        print("chub already installed; skipping")
        return
    print("installing chub (context-hub CLI)...")
    if shutil.which("npm"):
        rc = subprocess.run(["npm", "install", "-g", "@aisuite/chub"]).returncode
        if rc == 0:
            print("chub installed via npm")
            return
    if shutil.which("pip"):
        rc = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "chub-context"]).returncode
        if rc == 0:
            print("chub installed via pip")
            return
    print("WARN: chub install failed; agents will surface a hint on first use",
          file=sys.stderr)


def main() -> int:
    p = argparse.ArgumentParser(
        prog="install.py",
        description="Book Kit cross-platform installer (stdlib only).",
    )
    p.add_argument("--target", default=".", help="target project directory (default: cwd)")
    p.add_argument("--global", dest="scope_global", action="store_true",
                   help="install skills to global OpenCode config")
    p.add_argument("--local", dest="scope_local", action="store_true",
                   help="install skills to project-local .opencode/ (default)")
    p.add_argument("--both", dest="scope_both", action="store_true",
                   help="install skills to both scopes")
    p.add_argument("--check-only", action="store_true",
                   help="verify manifest + source checksums; do not modify files")
    p.add_argument("--uninstall", action="store_true",
                   help="remove all engine files; preserve user-owned content")
    p.add_argument("--upgrade", action="store_true",
                   help="refresh engine files; preserve user-owned content")
    p.add_argument("--with-chub", action="store_true",
                   help="also install chub context-hub CLI")
    p.add_argument("--no-doctor", action="store_true",
                   help="skip preflight checks")
    p.add_argument("--copy-anyway", action="store_true",
                   help="force copy mode even when target == kit root (default: install-in-place)")
    args = p.parse_args()

    if args.uninstall:
        return cmd_uninstall(args)
    return cmd_install(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        sys.exit(2)