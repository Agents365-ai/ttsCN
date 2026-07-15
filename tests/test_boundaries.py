"""Chunker bracket-guard, per-platform chunk preparation, envelope shaping."""
import time

import pytest

import tts
from markers import restore_pauses


# ── Chunker bracket-guard ─────────────────────────────────────────────────

def test_hard_split_never_cuts_inside_marker():
    # "，" sits just before the marker, inside the lookback window; the ':'
    # inside [PAUSE:0p8] is the nearest soft punct when the buffer fills —
    # the guard must skip it and cut at the "，" instead.
    sentence = "好" * 11 + "，" + "[PAUSE:0p8]" + "好" * 10
    pieces = tts._hard_split(sentence, 20)
    assert len(pieces) > 1
    for piece in pieces:
        assert piece.count("[") == piece.count("]")
    assert sum(p.count("[PAUSE:0p8]") for p in pieces) == 1
    assert "".join(pieces).replace("，", "") == sentence.replace("，", "")


def test_chunk_text_keeps_protected_pause_whole():
    text = "今天天气很好，" * 5 + "[PAUSE:0p8]" + "明天也不错。"
    for chunk in tts.chunk_text(text, 30):
        assert chunk.count("[") == chunk.count("]")


# ── Per-platform chunk preparation ────────────────────────────────────────

TEXT = "你好世界，今天[PAUSE:0.5]天气不错(chuckle)。"


def test_prepare_chunks_plain_platform_strips_markers():
    chunks = tts._prepare_chunks("edge", TEXT, 2000, {})
    joined = "".join(chunks)
    assert "[PAUSE" not in joined
    assert "(chuckle)" not in joined
    assert "你好世界" in joined


def test_prepare_chunks_azure_keeps_markers():
    chunks = tts._prepare_chunks("azure", TEXT, 2000, {})
    joined = "".join(chunks)
    assert "[PAUSE:0.5]" in joined  # rendered to SSML later, in the adapter


def test_prepare_chunks_minimax_gate_on(monkeypatch):
    monkeypatch.setenv("MINIMAX_MODEL", "speech-2.8-hd")
    chunks = tts._prepare_chunks(
        "minimax", TEXT, 3000, {"世界": "shi4 jie4"})
    joined = "".join(chunks)
    assert "<#0.5#>" in joined
    assert "(chuckle)" in joined
    assert "世(shi4)界(jie4)" in joined


def test_prepare_chunks_minimax_gate_off(monkeypatch, capsys):
    monkeypatch.delenv("MINIMAX_MODEL", raising=False)
    chunks = tts._prepare_chunks("minimax", TEXT, 3000, {})
    joined = "".join(chunks)
    assert "<#0.5#>" in joined
    assert "(chuckle)" not in joined
    assert "sound tags stripped" in capsys.readouterr().err


# ── Envelope shaping with a fake backend ──────────────────────────────────

def _run_fake_synthesis(monkeypatch, tmp_path, synth_return):
    def fake_synth(chunks, config, output_file, output_format="wav"):
        with open(output_file, "wb") as f:
            f.write(b"RIFFfake")
        return synth_return

    captured = {}

    def fake_emit_success(data=None, started_at=None, **extra):
        captured["data"] = data
        raise SystemExit(0)

    monkeypatch.setattr(tts, "init_backend", lambda name: {})
    monkeypatch.setattr(tts, "get_synthesize_func", lambda name: fake_synth)
    monkeypatch.setattr(tts, "emit_success", fake_emit_success)

    out = tmp_path / "out.wav"
    args = tts.build_parser().parse_args(
        ["你好世界。", str(out), "--platform", "edge", "--format", "json"])
    with pytest.raises(SystemExit):
        tts._run(args, time.time(), json_mode=True)
    return captured["data"]


def test_envelope_includes_word_boundaries(monkeypatch, tmp_path):
    boundaries = [
        {"text": "你好", "offset": 0.0, "duration": 0.51236},
        {"text": "世界", "offset": 0.51236, "duration": 0.47001},
    ]
    data = _run_fake_synthesis(monkeypatch, tmp_path, (0.98237, boundaries))
    wb = data["word_boundaries"]
    assert wb == [
        {"text": "你好", "offset_sec": 0.0, "duration_sec": 0.512},
        {"text": "世界", "offset_sec": 0.512, "duration_sec": 0.47},
    ]
    assert wb[0]["offset_sec"] < wb[1]["offset_sec"]
    assert data["duration_seconds"] == 1.0


def test_envelope_omits_boundaries_for_float_return(monkeypatch, tmp_path):
    data = _run_fake_synthesis(monkeypatch, tmp_path, 1.5)
    assert "word_boundaries" not in data


def test_envelope_omits_boundaries_for_empty_list(monkeypatch, tmp_path):
    data = _run_fake_synthesis(monkeypatch, tmp_path, (1.5, []))
    assert "word_boundaries" not in data
