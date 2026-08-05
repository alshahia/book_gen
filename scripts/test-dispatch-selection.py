"""Phase 7 dispatch-selection smoke test.

Verifies the orchestrator's Phase 7 dispatch-selection logic reads
intake.md §10 correctly and routes to Branch A (translation-mode) or
Branch B (native book-gen) per the rules in agents_manager/book-gen-orchestrator/SKILL.md
"""

import re
from pathlib import Path
import subprocess
import sys
import tempfile


def dispatch_select(intake_path: Path, source_map_path: Path) -> str:
    """Replicates orchestrator Phase 7 dispatch-selection logic."""
    if not intake_path.exists():
        return "Branch B: 3-pass dev/line/copy (no intake.md — pre-v0.22.0 project)"
    intake = intake_path.read_text(encoding='utf-8')
    m = re.search(r'##\s*10\.\s*Translation mode.*?Is translation\?\s*\u2014\s*(yes|no)', intake, re.S | re.I)
    is_translation = m.group(1).strip().lower() == 'yes' if m else False
    smap = source_map_path
    if is_translation and smap.exists():
        return "Branch A: book-reviewer (2-pass accuracy + consistency)"
    elif is_translation and not smap.exists():
        return "REFUSE: §10 says yes but source-map.md missing - surface to user"
    return "Branch B: 3-pass dev/line/copy (native book-gen)"


def test(name: str, root: Path) -> str:
    """Run dispatch_select and return the routing decision."""
    return f"  {name}\n    {dispatch_select(root / 'intake.md', root / 'source-map.md')}"


# Real native project (no §10 in intake — pre-v0.22.0 schema)
real_native = Path("E:/book_gen/books/ai-agents-with-python")

# Synthetic test projects
def make_synthetic(label, with_intake_section10, is_translation, with_source_map):
    tmp = Path(tempfile.mkdtemp())
    (tmp / 'chapters').mkdir(exist_ok=True)
    if with_intake_section10:
        body = f"- [x] **Is translation? \u2014 {'yes' if is_translation else 'no'}\n"
        (tmp / 'intake.md').write_text(f"# Intake\n\n## 10. Translation mode\n\n{body}", encoding='utf-8')
    else:
        (tmp / 'intake.md').write_text("# Intake\n\n## 1. Title\n\nFoo\n", encoding='utf-8')
    if with_source_map:
        (tmp / 'source-map.md').write_text(
            "| chapter | source | word_min | word_max | required_h2 | freeze_code |\n"
            "|---|---|---:|---:|---|:-:|\n"
            "| ch-01.md | source/ch-01.txt | 50 | 200 | | yes |\n",
            encoding='utf-8')
    return tmp


# Scenarios
print("=" * 64)
print("Phase 7 dispatch-selection — smoke test (4 scenarios)")
print("=" * 64)
print()
print("Scenario 1: Real native book-gen (ai-agents-with-python)")
print(test("intake=no §10, source-map=missing", real_native))
print()

# Synthetic cases
trans_yes_with_map = make_synthetic("translation=yes+map", True, True, True)
print("Scenario 2: Synthetic translation-mode (intake §10=yes, source-map=present)")
print(test(f"intake=yes, source-map=present", trans_yes_with_map))
print()

trans_yes_no_map = make_synthetic("translation=yes+no_map", True, True, False)
print("Scenario 3: Translation-mode intent, source-map.md MISSING")
print(test("intake=yes, source-map=missing", trans_yes_no_map))
print()

trans_no_with_map = make_synthetic("translation=no+map", True, False, True)
print("Scenario 4: Translation=no, source-map.md present (stray file)")
print(test("intake=no, source-map=present", trans_no_with_map))
print()

# book_check.py on native project
print("=" * 64)
print("book_check.py on ai-agents-with-python (verify no false positives)")
print("=" * 64)
result = subprocess.run(
    [r"E:/book_gen/.venv/Scripts/python.exe",
     r"E:/book_gen/book_workflow/scripts/book_check.py",
     "E:/book_gen/books/ai-agents-with-python"],
    capture_output=True, text=True)
print(f"  exit code: {result.returncode}")
last_stderr_line = result.stderr.strip().split('\n')[-1] if result.stderr.strip() else '(empty)'
print(f"  stderr: {last_stderr_line}")
print(f"  {'PASS' if result.returncode == 0 else 'FAIL'} — book_check did not false-positive on native book-gen")
