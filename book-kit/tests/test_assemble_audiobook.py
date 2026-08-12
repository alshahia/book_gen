"""Tests for assemble_audiobook.py -- Phase 4a M4B assembler.

Covers four required behaviours per the Phase 4a dispatch contract:

  (a) happy-path on a stub MP3 set (full concat -> M4B; skipped when
      ffmpeg or ffprobe is absent from PATH);
  (b) cover-resolution fallback ladder (figures/cover.png wins over
      chapters-rendered/*.png; all tiers missing raises exit 2);
  (c) path validation rejects '..' in --book and --out (exit 2);
  (d) ID3 metadata propagation -- genre=Audiobook, title, artist appear
      in the produced M4B's format_tags (skipped when ffprobe absent).

Plus a --help smoke test (exit 0) and a chapter-title parse check that
runs without ffmpeg.

Phase 4a-fix additions (P6T2 plan bullets that the prior dispatch
de-scoped): two-pass loudnorm, style-guide chapter titles, voice-policy
enforcement, --self-check chapter-count assertion.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Path setup: inline SCRIPTS sys.path (per "no conftest" rule). Mirror
# the pattern used by test_errors.py for the lib/ path.
# ---------------------------------------------------------------------------

KIT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = KIT_ROOT / "book_workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import assemble_audiobook as asm_mod  # noqa: E402


# Module-level dep probes for skipif markers. We split ffmpeg vs ffprobe
# because some hosts ship one without the other; either being absent
# triggers a skip on the corresponding tests.
HAS_FFMPEG = shutil.which("ffmpeg") is not None
HAS_FFPROBE = shutil.which("ffprobe") is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# Minimal 1x1 PNG (89 bytes; decodes to a 1x1 RGBA pixel). Real cover
# images in production are larger; the bytes we need are only the magic
# header so file-existence tests work. ffmpeg copies the bytes verbatim
# onto the chpl atom -- it does not decode the cover image.
_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    + b"\x00\x00\x00\rIHDR"
    + b"\x00\x00\x00\x01\x00\x00\x00\x01"
    + b"\x08\x06\x00\x00\x00"
    + b"\x1f\x15\xc4\x89"
    + b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA"
    + b"\xb6\x0c\x82\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _write_minimal_png(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_PNG_BYTES)
    return path


def _make_chapter_md(book_dir, ch_id, title):
    """Create chapters/<ch_id>.md with the given H1 title (publish-stripped)."""
    chapters = book_dir / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    text = "# %s\n\nbody paragraph.\n" % title
    (chapters / ("%s.md" % ch_id)).write_text(text, encoding="utf-8")
    return chapters / ("%s.md" % ch_id)


def _make_silence_mp3(path, duration_seconds=1.0):
    """Generate a tiny mono MP3 of silence via ffmpeg's anullsrc lavfi.

    Used by the happy-path tests so we never depend on the real
    media_tts pipeline. Returns the absolute path.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not on PATH")
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-loglevel", "error",
        "-f", "lavfi",
        "-i", "anullsrc=channel_layout=mono:sample_rate=22050",
        "-t", str(duration_seconds),
        "-ac", "1", "-ar", "22050", "-b:a", "64k",
        "-codec:a", "libmp3lame",
        str(path),
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg lavfi failed: %s" % proc.stderr)
    return path


# ---------------------------------------------------------------------------
# 1) --help exits 0 (smoke test, no ffmpeg required).
# ---------------------------------------------------------------------------


def test_help_exits_zero():
    """`--help` exits 0 via argparse; we expect SystemExit(0)."""
    with pytest.raises(SystemExit) as exc:
        asm_mod.main(["--help"])
    assert exc.value.code == 0


# ---------------------------------------------------------------------------
# 2) Cover fallback ladder: tier-2 figures/cover.png wins over tier-3.
# ---------------------------------------------------------------------------


def test_resolve_cover_prefers_figures_cover_png(tmp_path, monkeypatch):
    """When figures/cover.png exists, it wins regardless of chapters-rendered/."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    primary = book / "figures" / "cover.png"
    _write_minimal_png(primary)
    # Stage a competing PNG that must NOT win.
    cr = book / "chapters-rendered"
    cr.mkdir()
    _write_minimal_png(cr / "fig-A.png")
    _write_minimal_png(cr / "fig-B.png")
    resolved = asm_mod._resolve_cover(book)
    assert resolved == primary.resolve()


# ---------------------------------------------------------------------------
# 3) Cover fallback ladder: tier-3 chapters-rendered/ first PNG (sorted).
# ---------------------------------------------------------------------------


def test_resolve_cover_falls_back_to_chapters_rendered_png(tmp_path, monkeypatch):
    """When figures/cover.png is absent, the first sorted PNG in
    chapters-rendered/ wins."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    # Stage an empty figures dir (so tier 2 misses).
    (book / "figures").mkdir()
    cr = book / "chapters-rendered"
    cr.mkdir()
    _write_minimal_png(cr / "fig-B.png")
    _write_minimal_png(cr / "fig-A.png")  # alphabetically first -> wins
    resolved = asm_mod._resolve_cover(book)
    assert resolved == (cr / "fig-A.png").resolve()


# ---------------------------------------------------------------------------
# 4) Cover fallback ladder: all tiers missing -> raise exit 2 via catalog.
# ---------------------------------------------------------------------------


def test_resolve_cover_raises_exit_2_when_all_tiers_missing(tmp_path, monkeypatch):
    """When no cover candidate exists in any tier, the helper raises
    errors.raise_actionable('schema_invalid', ...) with exit_code=2."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    # Empty figures, no chapters-rendered dir -> both tiers miss.
    (book / "figures").mkdir()
    with pytest.raises(asm_mod.errors_mod.MediaPipelineError) as exc:
        asm_mod._resolve_cover(book)
    assert exc.value.exit_code == 2


# ---------------------------------------------------------------------------
# 5) Path validation: --book with '..' component -> exit 2.
# ---------------------------------------------------------------------------


def test_path_validation_rejects_dotdot_in_book(tmp_path, monkeypatch, capsys):
    """--book containing '..' exits 2 before any IO."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    rc = asm_mod.run_assemble("../escape", "en", None)
    captured = capsys.readouterr()
    assert rc == 2
    assert ".." in captured.err


# ---------------------------------------------------------------------------
# 6) Path validation: --out with '..' component -> exit 2.
# ---------------------------------------------------------------------------


def test_path_validation_rejects_dotdot_in_out(tmp_path, monkeypatch, capsys):
    """--out containing '..' exits 2 before any IO. --book is valid here
    so we can isolate the --out rejection (chapters/ is created so the
    pre-cover checks do not fire)."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    (book / "chapters").mkdir()
    # Cover still missing -- but we want --out to fire first; run_assemble
    # validates --book then --out then cover, so --out will be reached.
    rc = asm_mod.run_assemble(str(book), "en", "../escape.m4b")
    captured = capsys.readouterr()
    assert rc == 2
    assert ".." in captured.err


# ---------------------------------------------------------------------------
# 7) Path validation: --out that escapes repo root via absolute path -> exit 2.
# ---------------------------------------------------------------------------


def test_path_validation_rejects_absolute_out_outside_repo(tmp_path, monkeypatch, capsys):
    """Absolute --out that resolves outside REPO_ROOT exits 2."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    (book / "chapters").mkdir()
    # On Windows an absolute path like C:\\Windows\\Temp\\x.m4b resolves
    # outside the (monkeypatched) repo root -- the guard must reject it.
    rc = asm_mod.run_assemble(str(book), "en", "C:\\Windows\\Temp\\x.m4b")
    captured = capsys.readouterr()
    assert rc == 2
    assert "must resolve under" in captured.err


# ---------------------------------------------------------------------------
# 8) Happy-path: full assembler end-to-end (skipped when ffmpeg/ffprobe absent).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (HAS_FFMPEG and HAS_FFPROBE),
    reason="ffmpeg and/or ffprobe not on PATH",
)
def test_happy_path_assembles_m4b(tmp_path, monkeypatch):
    """Stage a stub book (cover, 2 chapters, 2 silence MP3s) and run the
    full assembler. Expects exit 0 and a non-empty M4B at --out.

    Uses --no-loudnorm so the two-pass loudnorm overhead is skipped on
    the smoke target (the dispatch allows this; production still
    defaults to loudnorm ON)."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    # Cover (tier 2).
    _write_minimal_png(book / "figures" / "cover.png")
    # Chapters + audio.
    _make_chapter_md(book, "ch-01", "Chapter One")
    _make_chapter_md(book, "ch-02", "Chapter Two")
    _make_silence_mp3(book / "chapters" / "ch-01-en.mp3", duration_seconds=1.0)
    _make_silence_mp3(book / "chapters" / "ch-02-en.mp3", duration_seconds=1.0)
    out_path = book / "exports" / "demo-en.m4b"
    rc = asm_mod.run_assemble(str(book), "en", str(out_path), no_loudnorm=True)
    assert rc == 0, "expected exit 0, got %d" % rc
    assert out_path.exists()
    assert out_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# 9) ID3 metadata propagation: title/artist/genre appear in the M4B
#    (skipped when ffprobe absent).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (HAS_FFMPEG and HAS_FFPROBE),
    reason="ffmpeg and/or ffprobe not on PATH",
)
def test_id3_metadata_propagation(tmp_path, monkeypatch):
    """Verify the M4B carries the metadata the dispatch contract demands:
    title/artist/album/genre land in format_tags, and the audio track's
    mdhd atom carries the locale (ffmpeg drops format-level language
    for the mp4 muxer, so we test the stream-level tag instead).

    Uses --no-loudnorm (smoke target; two-pass is irrelevant to ID3
    propagation)."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    _write_minimal_png(book / "figures" / "cover.png")
    _make_chapter_md(book, "ch-01", "Chapter One")
    _make_silence_mp3(book / "chapters" / "ch-01-en.mp3", duration_seconds=1.0)
    out_path = book / "exports" / "demo-en.m4b"
    rc = asm_mod.run_assemble(str(book), "en", str(out_path), no_loudnorm=True)
    assert rc == 0
    ffprobe = shutil.which("ffprobe")
    # Format-level tags: title/artist/album/genre=Audiobook.
    fmt_proc = subprocess.run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format_tags",
            "-of", "default=noprint_wrappers=0",
            str(out_path),
        ],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert fmt_proc.returncode == 0, "ffprobe format_tags failed: %s" % fmt_proc.stderr
    fmt_meta = fmt_proc.stdout
    assert "Audiobook" in fmt_meta, "genre=Audiobook missing from M4B metadata"
    # Title/artist fall back to book_dir.name / "Unknown" since intake.md
    # is not staged -- so we expect the slug "demo" as title and the
    # literal "Unknown" as artist.
    assert "title=demo" in fmt_meta, "title (slug fallback) missing"
    assert "artist=Unknown" in fmt_meta, "artist fallback missing"
    # Stream-level tags: language lives in the audio track's mdhd atom.
    stream_proc = subprocess.run(
        [
            ffprobe, "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream_tags=language",
            "-of", "default=noprint_wrappers=0",
            str(out_path),
        ],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert stream_proc.returncode == 0, "ffprobe stream_tags failed: %s" % stream_proc.stderr
    stream_meta = stream_proc.stdout
    assert "language=eng" in stream_meta, (
        "audio track language=eng (from locale=en) missing from stream tags: %r"
        % stream_meta
    )


# ---------------------------------------------------------------------------
# 10) Chapter title parse: H1 is read + publish-comment stripped (no ffmpeg).
# ---------------------------------------------------------------------------


def test_chapter_title_strips_publish_comment_and_reads_h1(tmp_path):
    """The chapter-title helper must skip HTML comments and read the H1."""
    book = tmp_path / "books" / "demo"
    (book / "chapters").mkdir(parents=True)
    md_path = book / "chapters" / "ch-01.md"
    md_path.write_text(
        "<!-- Self-critique: drafted -->\n"
        "\n"
        "# The Real Title\n"
        "\n"
        "Body.\n",
        encoding="utf-8",
    )
    title = asm_mod._chapter_title(book, "ch-01")
    assert title == "The Real Title"


# ---------------------------------------------------------------------------
# 11) Chapter id discovery: sorted numeric order (no ffmpeg).
# ---------------------------------------------------------------------------


def test_load_chapter_ids_returns_sorted_ch_ids(tmp_path):
    """ch-10.md must sort AFTER ch-02.md (numeric, not lex)."""
    book = tmp_path / "books" / "demo"
    chapters = book / "chapters"
    chapters.mkdir(parents=True)
    for n in ("01", "10", "02"):
        (chapters / ("ch-%s.md" % n)).write_text("# t\n", encoding="utf-8")
    ids = asm_mod._load_chapter_ids(book)
    assert ids == ["ch-01", "ch-02", "ch-10"]


# ---------------------------------------------------------------------------
# 12) Per-chapter MP3 resolution via Tier 2 fallback (chapters/<id>-<loc>.mp3).
# ---------------------------------------------------------------------------


def test_find_chapter_audio_tier2_fallback(tmp_path, monkeypatch):
    """Without a manifest, _find_chapter_audio should resolve the raw
    chapters/<id>-<locale>.mp3 layout."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    chapters = book / "chapters"
    chapters.mkdir(parents=True)
    mp3 = chapters / "ch-01-en.mp3"
    mp3.write_bytes(b"ID3" + b"\x00" * 16)  # placeholder bytes
    resolved = asm_mod._find_chapter_audio(book, "ch-01", "en")
    assert resolved == mp3.resolve()


# ---------------------------------------------------------------------------
# 13) Missing chapter audio raises InputError -> exit 2 (no ffmpeg).
# ---------------------------------------------------------------------------


def test_find_chapter_audio_missing_raises(tmp_path, monkeypatch, capsys):
    """Without manifest and without chapters/<id>-<locale>.mp3, the
    helper raises InputError; run_assemble maps that to exit 2."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    (book / "chapters").mkdir(parents=True)
    _make_chapter_md(book, "ch-01", "Chapter One")
    _write_minimal_png(book / "figures" / "cover.png")
    out_path = book / "exports" / "demo-en.m4b"
    rc = asm_mod.run_assemble(str(book), "en", str(out_path))
    captured = capsys.readouterr()
    assert rc == 2
    assert "no MP3 found" in captured.err


# ---------------------------------------------------------------------------
# 14) --help still exits 0 when --no-loudnorm + --self-check are present.
#     argparse parses them fine; --help short-circuits before any work.
# ---------------------------------------------------------------------------


def test_help_with_new_flags_exits_zero(capsys):
    """--help + --no-loudnorm + --self-check must still exit 0.

    argparse rejects unknown options; the test guards against accidental
    flag-renames in the parser.
    """
    with pytest.raises(SystemExit) as exc:
        asm_mod.main(["--help", "--no-loudnorm", "--self-check"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "--no-loudnorm" in captured.out
    assert "--self-check" in captured.out


# ---------------------------------------------------------------------------
# 15) Two-pass loudnorm: monkeypatches subprocess.run to capture argv and
#     asserts the measure pass + apply pass contain the canonical tokens.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg not on PATH")
def test_loudnorm_two_pass_invoked_when_enabled(tmp_path, monkeypatch):
    """When --no-loudnorm is NOT set, the measure + apply passes both
    run. We capture every subprocess.run argv and assert the measure
    pass contains `loudnorm=I=-19:TP=-2:LRA=11:print_format=json` and
    the apply pass contains `measured_I=...`, `measured_TP=...`,
    `measured_LRA=...` (the plan's required tokens)."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    _write_minimal_png(book / "figures" / "cover.png")
    _make_chapter_md(book, "ch-01", "Chapter One")
    _make_silence_mp3(book / "chapters" / "ch-01-en.mp3", duration_seconds=1.0)
    out_path = book / "exports" / "demo-en.m4b"

    captured_argvs = []
    captured_returns = {
        # The loudnorm measure pass returns a JSON payload in stderr.
        "loudnorm_measure": type("R", (), {
            "returncode": 0,
            "stderr": (
                '{"input_i": -23.0, "input_tp": -1.0, "input_lra": 1.0, '
                '"input_thresh": -34.0, "target_offset": -0.5, '
                '"output_i": -19.0, "output_tp": -2.0, '
                '"output_lra": 11.0, "output_thresh": -34.0, "normalization_type": "linear"}'
            ),
            "stdout": "",
        })(),
        # The ffprobe duration probe returns a numeric duration.
        "ffprobe_duration": type("R", (), {
            "returncode": 0,
            "stderr": "",
            "stdout": "1.000000",
        })(),
        # The M4B muxer + loudnorm apply passes just need rc=0.
        "default": type("R", (), {
            "returncode": 0,
            "stderr": "",
            "stdout": "",
        })(),
    }

    real_run = asm_mod.subprocess.run

    def fake_run(cmd, *args, **kwargs):
        cmd_str = " ".join(str(x) for x in cmd)
        captured_argvs.append(cmd)
        if "print_format=json" in cmd_str and "loudnorm=I=" in cmd_str:
            r = captured_returns["loudnorm_measure"]
        elif "ffprobe" in cmd_str and "show_entries" in cmd_str and "format=duration" in cmd_str:
            r = captured_returns["ffprobe_duration"]
        else:
            r = captured_returns["default"]
        return r

    monkeypatch.setattr(asm_mod.subprocess, "run", fake_run)
    rc = asm_mod.run_assemble(str(book), "en", str(out_path))
    assert rc == 0, "expected exit 0, got %d" % rc

    # Find the measure pass + apply pass in the captured argv list.
    measure_argv = None
    apply_argv = None
    for argv in captured_argvs:
        s = " ".join(str(x) for x in argv)
        if "print_format=json" in s and "loudnorm=I=" in s:
            measure_argv = argv
        elif "measured_I=" in s and "linear=true" in s:
            apply_argv = argv
    assert measure_argv is not None, (
        "expected a loudnorm measure pass with print_format=json; got argvs: %r"
        % captured_argvs
    )
    assert apply_argv is not None, (
        "expected a loudnorm apply pass with measured_I=/linear=true; got argvs: %r"
        % captured_argvs
    )
    measure_str = " ".join(str(x) for x in measure_argv)
    apply_str = " ".join(str(x) for x in apply_argv)
    assert "loudnorm=I=-19:TP=-2:LRA=11:print_format=json" in measure_str
    assert "measured_I=" in apply_str
    assert "measured_TP=" in apply_str
    assert "measured_LRA=" in apply_str
    # Silence the unused-binding warning for the patched real_run alias.
    del real_run


# ---------------------------------------------------------------------------
# 16) --no-loudnorm: neither measure nor apply pass runs.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg not on PATH")
def test_loudnorm_skipped_with_no_loudnorm_flag(tmp_path, monkeypatch):
    """When --no-loudnorm is set, neither loudnorm pass runs; the M4B
    muxer reads the raw concat list directly. We still monkeypatch
    subprocess.run so the test runs without producing a real M4B."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    _write_minimal_png(book / "figures" / "cover.png")
    _make_chapter_md(book, "ch-01", "Chapter One")
    _make_silence_mp3(book / "chapters" / "ch-01-en.mp3", duration_seconds=1.0)
    out_path = book / "exports" / "demo-en.m4b"

    captured_argvs = []
    real_run = asm_mod.subprocess.run

    def fake_run(cmd, *args, **kwargs):
        captured_argvs.append(cmd)
        if "ffprobe" in " ".join(str(x) for x in cmd) and "format=duration" in " ".join(str(x) for x in cmd):
            return type("R", (), {
                "returncode": 0, "stderr": "", "stdout": "1.000000",
            })()
        return type("R", (), {
            "returncode": 0, "stderr": "", "stdout": "",
        })()

    monkeypatch.setattr(asm_mod.subprocess, "run", fake_run)
    rc = asm_mod.run_assemble(str(book), "en", str(out_path), no_loudnorm=True)
    assert rc == 0
    for argv in captured_argvs:
        s = " ".join(str(x) for x in argv)
        assert "loudnorm=I=" not in s, (
            "loudnorm should not be invoked when --no-loudnorm is set; saw: %s" % s
        )
        assert "measured_I=" not in s
        assert "print_format=json" not in s
    del real_run


# ---------------------------------------------------------------------------
# 17) style-guide `## Chapter titles` -> title list of the expected length.
# ---------------------------------------------------------------------------


def test_chapter_titles_from_style_guide_md(tmp_path):
    """A style-guide.md with `## Chapter titles` and N `- "Title"` entries
    produces an N-element list when N == expected chapter count."""
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    (book / "chapters").mkdir(parents=True)
    sg = book / "style-guide.md"
    sg.write_text(
        "# Style guide\n"
        "\n"
        "## Chapter titles\n"
        "\n"
        '- "Chapter 1: The Hook"\n'
        '- "Chapter 2: The Turn"\n'
        '- "Chapter 3: The Payoff"\n'
        "\n"
        "## Other section\n"
        "\n"
        "Not the chapter titles.\n",
        encoding="utf-8",
    )
    titles = asm_mod._style_guide_chapter_titles(book, expected_count=3)
    assert titles == [
        "Chapter 1: The Hook",
        "Chapter 2: The Turn",
        "Chapter 3: The Payoff",
    ]


# ---------------------------------------------------------------------------
# 18) Without a `## Chapter titles` section, run_assemble falls back to
#     the H1 of each chapters/ch-NN.md.
# ---------------------------------------------------------------------------


def test_chapter_titles_fallback_to_h1(tmp_path, monkeypatch):
    """When the style-guide section is missing OR has fewer entries than
    chapters, the assembler falls back to the H1 of each chapter file
    (the prior dispatch's behaviour, preserved)."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    (book / "chapters").mkdir(parents=True)
    # No style-guide.md at all -- first fallback path.
    _make_chapter_md(book, "ch-01", "First H1")
    _make_chapter_md(book, "ch-02", "Second H1")
    titles = asm_mod._style_guide_chapter_titles(book, expected_count=2)
    assert titles is None
    # Per-chapter helper still returns the H1 directly.
    assert asm_mod._chapter_title(book, "ch-01") == "First H1"
    assert asm_mod._chapter_title(book, "ch-02") == "Second H1"

    # A style-guide.md with `## Chapter titles` that is too short also
    # falls back (returns None rather than a truncated list).
    (book / "style-guide.md").write_text(
        "## Chapter titles\n\n- \"Only one\"\n",
        encoding="utf-8",
    )
    assert asm_mod._style_guide_chapter_titles(book, expected_count=2) is None


# ---------------------------------------------------------------------------
# 19) Voice-policy mismatch -> exit 2 + stderr mentions voice_unavailable.
# ---------------------------------------------------------------------------


def test_voice_policy_rejects_mismatch(tmp_path, monkeypatch, capsys):
    """When media-locale-manifest.json::products[locale=='en'].voice
    disagrees with figures/media-tts-manifest.json::chunks[].voice, the
    assembler exits 2 with the `voice_unavailable` hint on stderr."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    # Media-locale manifest: en audiobook says voice=af_heart.
    media_manifest = book / "media-locale-manifest.json"
    media_manifest.write_text(
        json.dumps({
            "source_locale": "en",
            "target_locales": ["en"],
            "products": [
                {
                    "id": "audiobook-en",
                    "locale": "en",
                    "format": "audio/m4b",
                    "tts_provider": "kokoro",
                    "voice": "af_heart",
                    "skip": False,
                }
            ],
        }),
        encoding="utf-8",
    )
    # TTS manifest: chapters were synthesised with a DIFFERENT voice.
    tts_manifest = book / "figures" / "media-tts-manifest.json"
    tts_manifest.parent.mkdir(parents=True, exist_ok=True)
    tts_manifest.write_text(
        json.dumps({
            "chunks": [
                {
                    "chapter": "ch-01",
                    "locale": "en",
                    "voice": "am_adam",  # manifest says af_heart -> mismatch
                    "tts_provider": "kokoro",
                }
            ]
        }),
        encoding="utf-8",
    )
    # Calling the helper directly raises MediaPipelineError(exit_code=2).
    with pytest.raises(asm_mod.errors_mod.MediaPipelineError) as exc:
        asm_mod._enforce_voice_policy(book, "en")
    assert exc.value.exit_code == 2
    # The format_hint('voice_unavailable', ...) hint template produces
    # a string like "voice 'am_adam' not registered for locale='en' via
    # provider='af_heart'; ...". Assert on the canonical fragments.
    hint_text = str(exc.value)
    assert "voice 'am_adam' not registered" in hint_text
    assert "locale='en'" in hint_text
    # And via run_assemble the return code is also 2 + stderr mentions
    # the canonical hint.
    rc = asm_mod.run_assemble(
        str(book), "en", str(book / "exports" / "demo-en.m4b"),
        no_loudnorm=True,
    )
    captured = capsys.readouterr()
    assert rc == 2
    assert "not registered" in captured.err or "voice" in captured.err.lower()


# ---------------------------------------------------------------------------
# 20) --self-check chapter count mismatch -> exit 4 + stderr mentions
#     `audio_empty` (via the `lib.errors` format_hint catalog).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_FFPROBE, reason="ffprobe not on PATH")
def test_self_check_chapter_count_mismatch_fails(tmp_path, monkeypatch, capsys):
    """When the M4B exists but its chapter count != product_count,
    --self-check exits 4 with the audio_empty hint on stderr."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    out_path = book / "exports" / "demo-en.m4b"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(b"FAKEM4B")  # placeholder; ffprobe only sees JSON.
    # TTS manifest: 2 chapter rows -> expected=2.
    tts_manifest = book / "figures" / "media-tts-manifest.json"
    tts_manifest.parent.mkdir(parents=True, exist_ok=True)
    tts_manifest.write_text(
        json.dumps({
            "chunks": [
                {"chapter": "ch-01", "locale": "en", "voice": "af_heart"},
                {"chapter": "ch-02", "locale": "en", "voice": "af_heart"},
            ]
        }),
        encoding="utf-8",
    )
    # ffprobe stub: returns 0 chapters; expected is 2.
    real_run = asm_mod.subprocess.run

    def fake_run(cmd, *args, **kwargs):
        cmd_str = " ".join(str(x) for x in cmd)
        if "show_chapters" in cmd_str:
            return type("R", (), {
                "returncode": 0,
                "stderr": "",
                "stdout": '{"chapters": []}',  # 0 chapters -> mismatch
            })()
        if "format_tags" in cmd_str:
            return type("R", (), {
                "returncode": 0,
                "stderr": "",
                "stdout": "demo",
            })()
        return type("R", (), {
            "returncode": 0, "stderr": "", "stdout": "",
        })()

    monkeypatch.setattr(asm_mod.subprocess, "run", fake_run)
    with pytest.raises(asm_mod.errors_mod.MediaPipelineError) as exc:
        asm_mod._self_check(out_path, book, "en", "demo")
    assert exc.value.exit_code == 4
    # The audio_empty hint text mentions "synthesized audio was empty"
    # -- assert on that instead of the catalog key (the helper does not
    # leak the internal error_kind on the exception).
    assert "synthesized audio was empty" in str(exc.value)
    del real_run


# ---------------------------------------------------------------------------
# 21) --self-check locale filter: TTS manifest with mixed locales counts
#     only the rows for the current locale. With locale=ar, expected=1
#     even though the manifest has 3 (chapter, locale) entries.
# ---------------------------------------------------------------------------


def test_expected_chapter_count_filters_by_locale(tmp_path, monkeypatch):
    """TTS manifest with en+ar entries: expected count is scoped to locale."""
    monkeypatch.setattr(asm_mod, "REPO_ROOT", tmp_path)
    book = tmp_path / "books" / "demo"
    book.mkdir(parents=True)
    # 2 en + 1 ar = 3 total entries.
    tts_manifest = book / "figures" / "media-tts-manifest.json"
    tts_manifest.parent.mkdir(parents=True, exist_ok=True)
    tts_manifest.write_text(
        json.dumps({
            "chunks": [
                {"chapter": "ch-01", "locale": "en", "voice": "af_heart"},
                {"chapter": "ch-02", "locale": "en", "voice": "af_heart"},
                {"chapter": "ch-01", "locale": "ar", "voice": "ar-SA-HamedNeural"},
            ]
        }),
        encoding="utf-8",
    )
    assert asm_mod._expected_chapter_count(book, "en") == 2
    assert asm_mod._expected_chapter_count(book, "ar") == 1
    # No TTS manifest at all -> falls back to ch-*.md count.
    (book / "figures" / "media-tts-manifest.json").unlink()
    (book / "chapters").mkdir(parents=True, exist_ok=True)
    (book / "chapters" / "ch-01.md").write_text("x", encoding="utf-8")
    (book / "chapters" / "ch-02.md").write_text("x", encoding="utf-8")
    assert asm_mod._expected_chapter_count(book, "en") == 2
    assert asm_mod._expected_chapter_count(book, "ar") == 2
