"""Tests for assemble_video_horizontal.py -- Phase 4b Mode-1 horizontal video assembler.

Covers the CLI surface (help, exit codes on bad input), the cover-fallback
ladder helper, the ffmpeg argv + filter builders (with subprocess mocked),
and an end-to-end happy-path with --all that exercises the full pipeline
including sidecar manifest emission.

Helper names confirmed against the on-disk source:
  - _resolve_cover  (cover-fallback ladder; raises InputError on miss)
  - _build_ffmpeg_argv  (pure argv builder; no I/O)
  - _build_filter_arg  (filter_complex string; embeds shaping=complex
                        only when burn_subs and subs_path are set)
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

FFMPEG_PRESENT = shutil.which("ffmpeg") is not None
skipif_no_ffmpeg = pytest.mark.skipif(
    not FFMPEG_PRESENT, reason="ffmpeg system dep absent"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "book_workflow" / "scripts"))

import assemble_video_horizontal as avh  # noqa: E402

# REPO_ROOT per the script's own logic: parents[3] of the script
# (book-kit/book_workflow/scripts/assemble_video_horizontal.py). For the
# *test* file, which lives at book-kit/tests/, parents[2] lands on the
# repo root, so we use that and rebuild the script path from it.
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "book-kit" / "book_workflow" / "scripts" / "assemble_video_horizontal.py"
)

# Minimal 1x1 RGBA PNG. ffmpeg copies the bytes verbatim onto the MP4
# stream; we only need a valid header so the file-existence checks pass.
_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    + b"\x00\x00\x00\rIHDR"
    + b"\x00\x00\x00\x01\x00\x00\x00\x01"
    + b"\x08\x06\x00\x00\x00"
    + b"\x1f\x15\xc4\x89"
    + b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA"
    + b"\xb6\x0c\x82\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _write_minimal_png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_PNG_BYTES)
    return path


def _run_cli(args, timeout: int = 60) -> subprocess.CompletedProcess:
    """Invoke the script as a subprocess; return the CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )


@pytest.fixture
def book_under_repo():
    """A real book directory under REPO_ROOT so path-under-root checks pass.

    Lives under <repo>/books/__test_video_horizontal_<pid>/ and is removed
    on teardown. Re-running the test reclaims a stale dir from a prior
    interrupted run.
    """
    base = REPO_ROOT / "books" / f"__test_video_horizontal_{os.getpid()}"
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---------------------------------------------------------------------------
# T1: --help exits 0 and lists every required flag.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t1_help_lists_all_flags():
    result = _run_cli(["--help"])
    assert result.returncode == 0, f"--help failed; stderr={result.stderr!r}"
    for flag in (
        "--book",
        "--chapter",
        "--all",
        "--out",
        "--cover",
        "--audio",
        "--locale",
        "--bgm",
        "--burn-subs",
        "--subs",
    ):
        assert flag in result.stdout, f"flag {flag} absent from --help output"


# ---------------------------------------------------------------------------
# T2: missing --book exits 2 with non-empty stderr.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t2_missing_book_exits_2():
    result = _run_cli([
        "--out", "books/dummy/exports/x.mp4",
        "--locale", "en",
        "--chapter", "ch-01",
        "--audio", "books/dummy/exports/audio.m4b",
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""


# ---------------------------------------------------------------------------
# T3: --chapter and --all together (mutually exclusive) exits 2.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t3_chapter_and_all_mutually_exclusive():
    result = _run_cli([
        "--book", "books/dummy",
        "--out", "books/dummy/exports/x.mp4",
        "--locale", "en",
        "--chapter", "ch-01",
        "--all",
        "--audio", "books/dummy/exports/audio.m4b",
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""


# ---------------------------------------------------------------------------
# T4: --burn-subs without --subs exits 2.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t4_burn_subs_without_subs(book_under_repo):
    result = _run_cli([
        "--book", str(book_under_repo),
        "--out", str(book_under_repo / "exports" / "x.mp4"),
        "--locale", "en",
        "--chapter", "ch-01",
        "--audio", str(book_under_repo / "exports" / "audio.m4b"),
        "--burn-subs",
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""
    assert "--burn-subs" in result.stderr or "burn-subs" in result.stderr.lower()


# ---------------------------------------------------------------------------
# T5: --book pointing at C:\Windows (out-of-root) exits 2.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t5_book_out_of_root_exits_2():
    result = _run_cli([
        "--book", r"C:\Windows",
        "--out", "books/dummy/exports/x.mp4",
        "--locale", "en",
        "--chapter", "ch-01",
        "--audio", "books/dummy/exports/audio.m4b",
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""


# ---------------------------------------------------------------------------
# T6: --out pointing at C:\Temp\foo.mp4 (out-of-root) exits 2.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t6_out_out_of_root_exits_2(book_under_repo):
    result = _run_cli([
        "--book", str(book_under_repo),
        "--out", r"C:\Temp\foo.mp4",
        "--locale", "en",
        "--chapter", "ch-01",
        "--audio", str(book_under_repo / "exports" / "audio.m4b"),
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""


# ---------------------------------------------------------------------------
# T7: no --cover and no fallback images -> exit 2 + "No cover image found".
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t7_missing_cover_exits_2(book_under_repo):
    # Real audio placeholder so the audio-existence check (step 6) passes
    # and the script reaches _resolve_cover (which is what we want to fire).
    (book_under_repo / "exports").mkdir(parents=True, exist_ok=True)
    (book_under_repo / "exports" / "audio.m4b").write_bytes(b"")
    # No figures/cover.png and no chapters-rendered/ -- ladder exhausts.
    result = _run_cli([
        "--book", str(book_under_repo),
        "--out", str(book_under_repo / "exports" / "x.mp4"),
        "--locale", "en",
        "--chapter", "ch-01",
        "--audio", str(book_under_repo / "exports" / "audio.m4b"),
    ])
    assert result.returncode == 2
    assert "No cover image found" in result.stderr


# ---------------------------------------------------------------------------
# T8: introspect _resolve_cover (no ffmpeg required).
# ---------------------------------------------------------------------------

def test_t8_resolve_cover_ladder(tmp_path):
    cover_helper = getattr(avh, "_resolve_cover", None)
    assert cover_helper is not None, (
        "expected helper '_resolve_cover' on assemble_video_horizontal; "
        "rename reconfirmed at review time"
    )

    # Case 1: figures/cover.png present -> that path wins.
    case1 = tmp_path / "case1"
    (case1 / "figures").mkdir(parents=True)
    primary = case1 / "figures" / "cover.png"
    _write_minimal_png(primary)
    result1 = cover_helper(case1, None)
    assert Path(result1).resolve() == primary.resolve()

    # Case 2: only chapters-rendered/*.png present -> first sorted PNG wins.
    case2 = tmp_path / "case2"
    cr = case2 / "chapters-rendered"
    cr.mkdir(parents=True)
    # Two PNGs; ensure sort order picks the lexicographically first.
    _write_minimal_png(cr / "b.png")
    first = cr / "a.png"
    _write_minimal_png(first)
    result2 = cover_helper(case2, None)
    assert Path(result2).resolve() == first.resolve()

    # Case 3: empty book dir -> InputError (mapped to exit 2 by run_assemble).
    case3 = tmp_path / "case3"
    case3.mkdir()
    with pytest.raises(avh.InputError):
        cover_helper(case3, None)


# ---------------------------------------------------------------------------
# T9: argv builder with a non-existent audio path. Documents actual behavior:
# the builder is a pure constructor; it does NOT validate audio existence.
# Audio existence is enforced later in _render_chapter / run_assemble.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t9_argv_builder_non_existent_audio(tmp_path):
    argv_builder = getattr(avh, "_build_ffmpeg_argv", None)
    assert argv_builder is not None, (
        "expected helper '_build_ffmpeg_argv' on assemble_video_horizontal"
    )
    cover = _write_minimal_png(tmp_path / "cover.png")
    audio = tmp_path / "nonexistent.m4b"  # intentionally absent
    out = tmp_path / "out.mp4"
    filter_arg = "scale=1920:1080"
    # No raise: the builder embeds the path verbatim and lets the later
    # render / run_assemble layer enforce existence.
    cmd = argv_builder(cover, audio, None, filter_arg, out)
    assert any(str(audio) in str(tok) for tok in cmd), (
        f"audio path missing from argv; got {cmd!r}"
    )


# ---------------------------------------------------------------------------
# T10: argv structure (mocked subprocess, mocked which).
# ---------------------------------------------------------------------------

def test_t10_argv_structure(tmp_path):
    cover = _write_minimal_png(tmp_path / "cover.png")
    audio = tmp_path / "audio.m4b"
    audio.write_bytes(b"")
    out = tmp_path / "out.mp4"
    filter_arg = "scale=1920:1080"
    with patch("assemble_video_horizontal.shutil.which", return_value="ffmpeg"), \
         patch("assemble_video_horizontal.subprocess.run") as mock_run:
        cmd = avh._build_ffmpeg_argv(cover, audio, None, filter_arg, out)
    # The builder itself never calls subprocess.run; the mock is a safety
    # net in case a future refactor moves the call into the builder.
    assert mock_run.call_count == 0
    # Structure assertions: ffmpeg path, -y, -i (cover + audio), libx264, aac.
    assert cmd[0] == "ffmpeg"
    assert "-y" in cmd
    assert cmd.count("-i") >= 2
    assert "libx264" in cmd
    assert "aac" in cmd
    # 1920 and 1080 live inside the single -filter_complex argv token
    # (e.g. "scale=1920:1080"), so they are not standalone list elements.
    # Join for substring search.
    cmd_joined = " ".join(str(t) for t in cmd)
    assert "1920" in cmd_joined, f"1920 missing from filter_arg: {cmd!r}"
    assert "1080" in cmd_joined, f"1080 missing from filter_arg: {cmd!r}"


# ---------------------------------------------------------------------------
# T11: --burn-subs toggles shaping=complex in the filter_complex token.
# ---------------------------------------------------------------------------

def test_t11_burn_subs_filter(tmp_path):
    subs = tmp_path / "subs.ass"
    subs.write_text("", encoding="utf-8")
    cover = _write_minimal_png(tmp_path / "cover.png")
    audio = tmp_path / "audio.m4b"
    audio.write_bytes(b"")
    out = tmp_path / "out.mp4"
    with patch("assemble_video_horizontal.shutil.which", return_value="ffmpeg"), \
         patch("assemble_video_horizontal.subprocess.run"):
        # burn_subs=True + subs_path provided -> shaping=complex in the
        # -filter_complex argv token.
        f1 = avh._build_filter_arg(
            audio_dur=10.0, burn_subs=True, subs_path=subs, bgm_path=None
        )
        argv1 = avh._build_ffmpeg_argv(cover, audio, None, f1, out)
        assert any("shaping=complex" in str(tok) for tok in argv1), (
            f"shaping=complex missing from burn_subs=True argv: {argv1!r}"
        )

        # burn_subs=False -> shaping=complex absent from the argv entirely.
        f2 = avh._build_filter_arg(
            audio_dur=10.0, burn_subs=False, subs_path=subs, bgm_path=None
        )
        argv2 = avh._build_ffmpeg_argv(cover, audio, None, f2, out)
        assert not any("shaping=complex" in str(tok) for tok in argv2), (
            f"shaping=complex leaked into burn_subs=False argv: {argv2!r}"
        )


# ---------------------------------------------------------------------------
# T12: end-to-end happy-path with --all; asserts exit 0 + sidecar manifest.
#
# The script's ffmpeg invocation uses the 4x supersample trick (scale to
# 8000px wide) which makes the zoompan render CPU-bound and slow on
# constrained hosts. To validate the script's *orchestration* logic
# (chapter discovery, cover fallback, argv assembly, concat wiring,
# manifest emission, exit code) without paying the render cost, this
# test runs the assembler in-process and mocks subprocess.run to
# simulate ffmpeg/ffprobe success. The mocked ffmpeg "writes" a stub
# output file at the path the script requested, so the downstream
# concat and manifest steps see realistic filesystem state.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t12_end_to_end_all(book_under_repo):
    # Minimal book layout: one chapter, one cover, one per-chapter audio.
    chapters = book_under_repo / "chapters"
    chapters.mkdir()
    (chapters / "ch-01.md").write_text("# Ch 1\n\nbody paragraph.\n", encoding="utf-8")
    exports = book_under_repo / "exports"
    exports.mkdir()
    figures = book_under_repo / "figures"
    figures.mkdir()

    # Cover image (1x1 PNG; the mock skips the actual decode).
    _write_minimal_png(figures / "cover.png")

    # Real audio fixture on disk so the per-chapter audio-existence check
    # in the script's step 6 passes before subprocess.run is even called.
    # The mock will intercept ffprobe and report a synthetic duration.
    audio_path = exports / "audiobook-ch-01.m4b"
    audio_path.write_bytes(b"\x00" * 64)

    out_path = exports / "video-horizontal-m1.mp4"

    def _fake_run(cmd, **kwargs):
        """Pretend ffprobe/ffmpeg succeeded; materialise the output file.

        Inspects the first argv element to distinguish ffprobe (return a
        fake 0.1s duration) from ffmpeg (touch the output file at the
        last argv position). Both return a CompletedProcess-shaped
        MagicMock with returncode=0.
        """
        from unittest.mock import MagicMock
        cmd_strs = [str(c) for c in cmd]
        head = cmd_strs[0].lower()
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        if "ffprobe" in head:
            result.stdout = "0.1\n"
            return result
        # ffmpeg: create the output file at the last argv position so the
        # concat stage sees a real file to concatenate.
        output_path = Path(cmd_strs[-1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x00" * 16)
        return result

    with patch("assemble_video_horizontal.subprocess.run", side_effect=_fake_run):
        rc = avh.run_assemble(
            book_arg=str(book_under_repo),
            chapter=None,
            all_mode=True,
            out_arg=str(out_path),
            cover_arg=None,
            audio_arg=None,
            locale="en",
        )

    assert rc == 0, f"run_assemble returned {rc}; expected 0"
    assert out_path.exists(), f"output MP4 not materialised at {out_path}"

    # Sidecar manifest: <book>/figures/media-video-manifest.json.
    manifest_path = figures / "media-video-manifest.json"
    assert manifest_path.exists(), f"sidecar manifest not written at {manifest_path}"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "chapters" in manifest
    assert len(manifest["chapters"]) == 1
    entry = manifest["chapters"][0]
    assert entry["chapter_id"] == "ch-01"
    assert entry["codec"] == "libx264"
    assert entry["width"] == 1920
    assert entry["height"] == 1080
