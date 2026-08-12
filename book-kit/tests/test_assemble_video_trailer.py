"""Tests for assemble_video_trailer.py -- Phase 4b-2 video trailer assembler.

Covers the CLI surface (help, exit codes on bad input), the cover-fallback
ladder helper, the path-traversal rejection in _resolve_under_root, the
ffmpeg argv + filter builders (with subprocess mocked), and an
end-to-end happy-path that exercises the full pipeline including sidecar
manifest emission. Also covers MissingDepError (-> exit 3) and
RuntimeFailure (-> exit 4) by patching shutil.which + subprocess.run.

Helper names confirmed against the on-disk source:
  - _resolve_under_root  (path validation; refuses '..' and out-of-root)
  - _resolve_cover       (cover-fallback ladder; raises InputError on miss)
  - _build_filter_arg    (filter_complex string; embeds shaping=complex
                          only when burn_subs and subs_path are set,
                          and amix=inputs=2 only when bgm_path is set)
  - _build_ffmpeg_argv   (pure argv builder; no I/O; audio_offset/audio_dur
                          are positional args for per-clip audio window)
  - _load_chapter_ids    (numeric-sorted ch-NN.md discovery)
  - _select_clips        (clip-selection pass; CHAR_BUDGET + TARGET_CHUNKS)
"""
# ---------------------------------------------------------------------------
# UTF-8 stdio force (mandatory block from dispatch preamble). MUST run
# before any import that could open a file with a non-ASCII path and
# before argparse (so help + error text never crash on cp1256/cp1252).
# ---------------------------------------------------------------------------

import sys
import io
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, io.UnsupportedOperation):
        pass


import json
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

FFMPEG_PRESENT = shutil.which("ffmpeg") is not None
skipif_no_ffmpeg = pytest.mark.skipif(
    not FFMPEG_PRESENT, reason="ffmpeg system dep absent"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "book_workflow" / "scripts"))

import assemble_video_trailer as avt  # noqa: E402

# REPO_ROOT per the script's own logic: parents[3] of the script
# (book-kit/book_workflow/scripts/assemble_video_trailer.py). For the
# *test* file, which lives at book-kit/tests/, parents[2] lands on the
# repo root, so we use that and rebuild the script path from it.
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "book-kit" / "book_workflow" / "scripts" / "assemble_video_trailer.py"
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

    Lives under <repo>/books/__test_video_trailer_<pid>/ and is removed
    on teardown. Re-running the test reclaims a stale dir from a prior
    interrupted run.
    """
    base = REPO_ROOT / "books" / f"__test_video_trailer_{os.getpid()}"
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
        "--out",
        "--cover",
        "--locale",
        "--bgm",
        "--burn-subs",
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
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""


# ---------------------------------------------------------------------------
# T3: --cover containing '..' exits 2 (path-traversal rejection).
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t3_cover_path_traversal_exits_2(book_under_repo):
    result = _run_cli([
        "--book", str(book_under_repo),
        "--out", str(book_under_repo / "exports" / "x.mp4"),
        "--locale", "en",
        "--cover", "../escape.png",
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""
    assert ".." in result.stderr or "must not contain" in result.stderr


# ---------------------------------------------------------------------------
# T4: --book pointing at C:\Windows (out-of-root) exits 2.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t4_book_out_of_root_exits_2():
    result = _run_cli([
        "--book", r"C:\Windows",
        "--out", "books/dummy/exports/x.mp4",
        "--locale", "en",
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""


# ---------------------------------------------------------------------------
# T5: --out pointing at C:\Temp\foo.mp4 (out-of-root) exits 2.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t5_out_out_of_root_exits_2(book_under_repo):
    result = _run_cli([
        "--book", str(book_under_repo),
        "--out", r"C:\Temp\foo.mp4",
        "--locale", "en",
    ])
    assert result.returncode == 2
    assert result.stderr.strip() != ""


# ---------------------------------------------------------------------------
# T6: no --cover and no fallback images -> exit 2 + "No cover image found".
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t6_missing_cover_exits_2(book_under_repo):
    # No figures/cover.png and no chapters-rendered/ -- ladder exhausts.
    # chapters/ dir is required so the script reaches the cover check;
    # otherwise _load_chapter_ids raises first.
    (book_under_repo / "chapters").mkdir(parents=True, exist_ok=True)
    (book_under_repo / "chapters" / "ch-01.md").write_text(
        "# Ch 1\n\nbody paragraph.\n", encoding="utf-8"
    )
    result = _run_cli([
        "--book", str(book_under_repo),
        "--out", str(book_under_repo / "exports" / "x.mp4"),
        "--locale", "en",
    ])
    assert result.returncode == 2
    assert "No cover image found" in result.stderr


# ---------------------------------------------------------------------------
# T7: introspect _resolve_cover (no ffmpeg required).
# ---------------------------------------------------------------------------

def test_t7_resolve_cover_ladder(tmp_path):
    cover_helper = getattr(avt, "_resolve_cover", None)
    assert cover_helper is not None, (
        "expected helper '_resolve_cover' on assemble_video_trailer; "
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

    # Case 3: empty book dir -> InputError (mapped to exit 2 by run_trailer).
    case3 = tmp_path / "case3"
    case3.mkdir()
    with pytest.raises(avt.InputError):
        cover_helper(case3, None)

    # Case 4: --cover flag pointing at an existing file under REPO_ROOT wins
    # (tier 1). The cover flag routes through _resolve_under_root, so the
    # path must live under REPO_ROOT for the script to accept it.
    case4 = tmp_path / "case4"
    (case4 / "figures").mkdir(parents=True)
    _write_minimal_png(case4 / "figures" / "cover.png")
    explicit = REPO_ROOT / "book-kit" / "tests" / "_explicit_cover_fixture.png"
    if explicit.exists():
        explicit.unlink()
    _write_minimal_png(explicit)
    try:
        result4 = cover_helper(case4, str(explicit))
        assert Path(result4).resolve() == explicit.resolve()
    finally:
        if explicit.exists():
            explicit.unlink()


# ---------------------------------------------------------------------------
# T8: introspect _resolve_under_root (no ffmpeg required). Documents the
# path-traversal rejection rules: any '..' component, or any absolute
# path that does not live under REPO_ROOT, raises InputError (-> exit 2).
# ---------------------------------------------------------------------------

def test_t8_resolve_under_root_path_traversal(tmp_path):
    resolver = getattr(avt, "_resolve_under_root", None)
    assert resolver is not None, (
        "expected helper '_resolve_under_root' on assemble_video_trailer"
    )

    # Path with '..' component -> InputError.
    with pytest.raises(avt.InputError):
        resolver("../escape.png", "--test")

    # Absolute path out of repo root -> InputError.
    with pytest.raises(avt.InputError):
        resolver("C:/Windows/System32/notepad.exe", "--test")

    # Path under REPO_ROOT (book-kit itself always exists) -> returns resolved.
    target = REPO_ROOT / "book-kit"
    resolved = resolver(str(target), "--test")
    assert Path(resolved).resolve() == target.resolve()


# ---------------------------------------------------------------------------
# T9: argv builder with a non-existent audio path. Documents actual behavior:
# the builder is a pure constructor; it does NOT validate audio existence.
# Audio existence is enforced later in _render_clip / run_trailer.
# ---------------------------------------------------------------------------

@skipif_no_ffmpeg
def test_t9_argv_builder_non_existent_audio(tmp_path):
    argv_builder = getattr(avt, "_build_ffmpeg_argv", None)
    assert argv_builder is not None, (
        "expected helper '_build_ffmpeg_argv' on assemble_video_trailer"
    )
    cover = _write_minimal_png(tmp_path / "cover.png")
    audio = tmp_path / "nonexistent.m4b"  # intentionally absent
    out = tmp_path / "out.mp4"
    filter_arg = "scale=1920:1080"
    # audio_offset=0.0, audio_dur=5.0 -- positional, used to select the
    # per-clip audio window from the per-chapter M4B.
    cmd = argv_builder(cover, audio, 0.0, 5.0, None, filter_arg, out)
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
    with patch("assemble_video_trailer.shutil.which", return_value="ffmpeg"), \
         patch("assemble_video_trailer.subprocess.run") as mock_run:
        cmd = avt._build_ffmpeg_argv(cover, audio, 0.0, 5.0, None, filter_arg, out)
    # The builder itself never calls subprocess.run; the mock is a safety
    # net in case a future refactor moves the call into the builder.
    assert mock_run.call_count == 0
    # Structure assertions: ffmpeg path, -y, -loop 1, two -i (cover + audio),
    # libx264, aac, -shortest.
    assert cmd[0] == "ffmpeg"
    assert "-y" in cmd
    assert "-loop" in cmd
    assert "1" in cmd
    assert cmd.count("-i") >= 2
    assert "libx264" in cmd
    assert "aac" in cmd
    assert "-shortest" in cmd
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
    with patch("assemble_video_trailer.shutil.which", return_value="ffmpeg"):
        # burn_subs=True + subs_path provided -> shaping=complex in the
        # -filter_complex string.
        f1 = avt._build_filter_arg(
            audio_dur=10.0, burn_subs=True, subs_path=subs, bgm_path=None
        )
        assert "shaping=complex" in f1, (
            f"shaping=complex missing from burn_subs=True filter: {f1!r}"
        )

        # burn_subs=False -> shaping=complex absent from the filter entirely.
        f2 = avt._build_filter_arg(
            audio_dur=10.0, burn_subs=False, subs_path=subs, bgm_path=None
        )
        assert "shaping=complex" not in f2, (
            f"shaping=complex leaked into burn_subs=False filter: {f2!r}"
        )


# ---------------------------------------------------------------------------
# T12: --bgm toggles amix=inputs=2 in the filter_complex token.
# ---------------------------------------------------------------------------

def test_t12_bgm_toggles_amix(tmp_path):
    bgm = tmp_path / "bgm.mp3"
    bgm.write_bytes(b"")
    with patch("assemble_video_trailer.shutil.which", return_value="ffmpeg"):
        # bgm_path provided -> amix=inputs=2 in the -filter_complex string.
        f1 = avt._build_filter_arg(
            audio_dur=10.0, burn_subs=False, subs_path=None, bgm_path=bgm
        )
        assert "amix=inputs=2" in f1, (
            f"amix=inputs=2 missing from bgm_path=<set> filter: {f1!r}"
        )

        # bgm_path=None -> amix=inputs=2 absent from the filter entirely.
        f2 = avt._build_filter_arg(
            audio_dur=10.0, burn_subs=False, subs_path=None, bgm_path=None
        )
        assert "amix=inputs=2" not in f2, (
            f"amix=inputs=2 leaked into bgm_path=None filter: {f2!r}"
        )


# ---------------------------------------------------------------------------
# T13: ffprobe missing -> exit 3 (MissingDepError mapped by run_trailer).
# Patches shutil.which to return None for ffprobe so _probe_duration_seconds
# raises MissingDepError before any ffmpeg invocation.
# ---------------------------------------------------------------------------

def test_t13_ffprobe_missing_exits_3(book_under_repo):
    chapters = book_under_repo / "chapters"
    chapters.mkdir()
    (chapters / "ch-01.md").write_text(
        "# Ch 1\n\nFirst paragraph of body.\n", encoding="utf-8"
    )
    exports = book_under_repo / "exports"
    exports.mkdir()
    _write_minimal_png(book_under_repo / "figures" / "cover.png")
    (exports / "audiobook-ch-01.m4b").write_bytes(b"\x00" * 64)
    out_path = exports / "trailer.mp4"

    real_which = shutil.which

    def fake_which(name):
        if name == "ffprobe":
            return None
        if name == "ffmpeg":
            return "ffmpeg"
        return real_which(name)

    with patch("assemble_video_trailer.shutil.which", side_effect=fake_which):
        rc = avt.run_trailer(
            book_arg=str(book_under_repo),
            out_arg=str(out_path),
            cover_arg=None,
            locale="en",
        )
    assert rc == 3, f"run_trailer returned {rc}; expected 3 for missing ffprobe"


# ---------------------------------------------------------------------------
# T14: ffmpeg non-zero exit -> exit 4 (RuntimeFailure mapped by run_trailer).
# Patches subprocess.run so ffprobe returns a duration but ffmpeg raises
# CalledProcessError. _run_ffmpeg converts to RuntimeFailure; run_trailer
# catches and returns 4.
# ---------------------------------------------------------------------------

def test_t14_ffmpeg_nonzero_exits_4(book_under_repo):
    chapters = book_under_repo / "chapters"
    chapters.mkdir()
    (chapters / "ch-01.md").write_text(
        "# Ch 1\n\nFirst paragraph of body.\n", encoding="utf-8"
    )
    exports = book_under_repo / "exports"
    exports.mkdir()
    _write_minimal_png(book_under_repo / "figures" / "cover.png")
    (exports / "audiobook-ch-01.m4b").write_bytes(b"\x00" * 64)
    out_path = exports / "trailer.mp4"

    def fake_run(cmd, **kwargs):
        cmd_strs = [str(c) for c in cmd]
        head = cmd_strs[0].lower()
        if "ffprobe" in head:
            result = MagicMock()
            result.returncode = 0
            result.stdout = "10.0\n"
            result.stderr = ""
            return result
        # ffmpeg: simulate a non-zero exit.
        raise subprocess.CalledProcessError(
            1, cmd_strs, stderr="synthetic ffmpeg failure"
        )

    def fake_which(name):
        if name == "ffprobe":
            return "/usr/bin/ffprobe"
        if name == "ffmpeg":
            return "/usr/bin/ffmpeg"
        return None

    with patch("assemble_video_trailer.shutil.which", side_effect=fake_which), \
         patch("assemble_video_trailer.subprocess.run", side_effect=fake_run):
        rc = avt.run_trailer(
            book_arg=str(book_under_repo),
            out_arg=str(out_path),
            cover_arg=None,
            locale="en",
        )
    assert rc == 4, f"run_trailer returned {rc}; expected 4 for ffmpeg non-zero"


# ---------------------------------------------------------------------------
# T15: end-to-end happy-path; asserts exit 0 + sidecar manifest schema.
#
# The trailer's ffmpeg invocation uses the supersample zoompan trick
# which makes the render CPU-bound and slow on constrained hosts. To
# validate the script's *orchestration* logic (chapter discovery, cover
# fallback, clip-selection, argv assembly, concat wiring, manifest
# emission, exit code) without paying the render cost, this test runs
# the assembler in-process and mocks subprocess.run to simulate
# ffprobe/ffmpeg success. The mocked ffmpeg "writes" a stub output
# file at the path the script requested, so the downstream concat and
# manifest steps see realistic filesystem state.
# ---------------------------------------------------------------------------

def test_t15_end_to_end_happy_path(book_under_repo):
    # Minimal book layout: one chapter with a single paragraph chunk,
    # one cover, one per-chapter audio. _select_clips picks the first
    # (and only) chunk within CHAR_BUDGET so we get a single-clip
    # trailer -- keeps the manifest assertions deterministic.
    chapters = book_under_repo / "chapters"
    chapters.mkdir()
    (chapters / "ch-01.md").write_text(
        "Single paragraph body of the trailer source.\n",
        encoding="utf-8",
    )
    exports = book_under_repo / "exports"
    exports.mkdir()
    figures = book_under_repo / "figures"
    figures.mkdir()

    _write_minimal_png(figures / "cover.png")

    # Real audio fixture on disk so the per-chapter audio-existence check
    # in _select_clips passes before subprocess.run is even called.
    # The mock will intercept ffprobe and report a synthetic duration.
    audio_path = exports / "audiobook-ch-01.m4b"
    audio_path.write_bytes(b"\x00" * 64)

    out_path = exports / "video-trailer.mp4"

    def _fake_run(cmd, **kwargs):
        """Pretend ffprobe/ffmpeg succeeded; materialise the output file.

        Inspects the first argv element to distinguish ffprobe (return a
        fake 10s duration) from ffmpeg (touch the output file at the
        last argv position). Both return a CompletedProcess-shaped
        MagicMock with returncode=0.
        """
        cmd_strs = [str(c) for c in cmd]
        head = cmd_strs[0].lower()
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        if "ffprobe" in head:
            result.stdout = "10.0\n"
            return result
        # ffmpeg: create the output file at the last argv position so the
        # concat stage sees a real file to concatenate.
        output_path = Path(cmd_strs[-1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x00" * 16)
        return result

    def fake_which(name):
        if name == "ffprobe":
            return "/usr/bin/ffprobe"
        if name == "ffmpeg":
            return "/usr/bin/ffmpeg"
        return None

    with patch("assemble_video_trailer.shutil.which", side_effect=fake_which), \
         patch("assemble_video_trailer.subprocess.run", side_effect=_fake_run):
        rc = avt.run_trailer(
            book_arg=str(book_under_repo),
            out_arg=str(out_path),
            cover_arg=None,
            locale="en",
        )

    assert rc == 0, f"run_trailer returned {rc}; expected 0"
    assert out_path.exists(), f"output MP4 not materialised at {out_path}"

    # Sidecar manifest: <book>/figures/media-trailer-manifest.json.
    manifest_path = figures / "media-trailer-manifest.json"
    assert manifest_path.exists(), f"sidecar manifest not written at {manifest_path}"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Top-level keys (per dispatch spec).
    assert "trailer" in manifest
    assert manifest["codec"] == "libx264"
    assert manifest["width"] == 1920
    assert manifest["height"] == 1080

    trailer = manifest["trailer"]
    assert "clips" in trailer
    assert len(trailer["clips"]) == 1
    assert trailer["codec"] == "libx264"
    assert trailer["width"] == 1920
    assert trailer["height"] == 1080
    assert trailer["target_chunks"] == 12
    assert trailer["char_budget"] == 1500
    assert trailer["locale"] == "en"
    assert trailer["burned_subs"] is False
    assert trailer["bgm"] is None
    assert isinstance(trailer["duration_s_total"], (int, float))
    assert trailer["duration_s_total"] > 0

    # Per-clip entry shape.
    entry = trailer["clips"][0]
    assert entry["chapter_id"] == "ch-01"
    assert entry["codec"] == "libx264"
    assert entry["width"] == 1920
    assert entry["height"] == 1080
    assert entry["clip_index"] == 0
    assert entry["burned_subs"] is False
    assert entry["bgm"] is None
    assert isinstance(entry["duration_s"], (int, float))
    assert isinstance(entry["char_count"], int)
    assert entry["char_count"] > 0
    assert isinstance(entry["audio_offset_s"], (int, float))