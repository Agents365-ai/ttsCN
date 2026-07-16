"""Chunker bracket-guard, per-platform chunk preparation, envelope shaping."""
import json
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


# ── Backend boundary parsers (doubao frontend / minimax subtitles) ────────

def test_doubao_frontend_words_parse():
    from backends.doubao import _parse_frontend_words
    frontend = json.dumps({
        "words": [
            {"word": "你", "start_time": 0.025, "end_time": 0.185},
            {"word": "好", "start_time": 0.185, "end_time": 0.36},
        ],
        "phonemes": [{"phone": "C0n", "start_time": 0.025, "end_time": 0.1}],
    })
    out = _parse_frontend_words(frontend, 10.0)
    assert out == [
        {"text": "你", "offset": 10.025, "duration": pytest.approx(0.16)},
        {"text": "好", "offset": 10.185, "duration": pytest.approx(0.175)},
    ]


def test_doubao_frontend_absent_or_malformed():
    from backends.doubao import _parse_frontend_words
    assert _parse_frontend_words(None, 0.0) == []
    assert _parse_frontend_words("", 0.0) == []
    assert _parse_frontend_words("not json", 0.0) == []
    assert _parse_frontend_words('{"words": [{"word": "x"}]}', 0.0) == []


def test_minimax_subtitles_parse_ms_to_sec():
    from backends.minimax import _parse_subtitles
    # Real payload shape (China site, subtitle_type=word): sentence blocks
    # with nested timestamped_words; punctuation gets its own entry.
    entries = [{
        "text": "你好，", "time_begin": 0.0, "time_end": 725.3,
        "timestamped_words": [
            {"word": "你", "time_begin": 42.7, "time_end": 213.3},
            {"word": "好", "time_begin": 213.3, "time_end": 341.3},
            {"word": "，", "time_begin": 341.3, "time_end": 725.3},
        ],
    }]
    out = _parse_subtitles(entries, 2.0)
    assert out == [
        {"text": "你", "offset": pytest.approx(2.0427),
         "duration": pytest.approx(0.1706)},
        {"text": "好", "offset": pytest.approx(2.2133),
         "duration": pytest.approx(0.128)},
        {"text": "，", "offset": pytest.approx(2.3413),
         "duration": pytest.approx(0.384)},
    ]


def test_minimax_subtitles_drop_engine_tokens():
    from backends.minimax import _parse_subtitles
    # Pinyin annotations 字(zi4) come back as one entry per phonetic symbol,
    # each with word="(zi4)"; sound tags behave the same. Only script chars
    # may survive into the boundary stream.
    entries = [{
        "timestamped_words": [
            {"word": "模", "time_begin": 128.0, "time_end": 298.7},
            {"word": "(mo2)", "time_begin": 298.7, "time_end": 426.7},
            {"word": "(mo2)", "time_begin": 426.7, "time_end": 512.0},
            {"word": "型", "time_begin": 512.0, "time_end": 597.3},
            {"word": "(chuckle)", "time_begin": 597.3, "time_end": 900.0},
        ],
    }]
    out = _parse_subtitles(entries, 0.0)
    assert [w["text"] for w in out] == ["模", "型"]


def test_cosyvoice_event_fold_last_wins():
    from backends.cosyvoice import _extract_words, _to_boundaries
    # words arrays grow progressively across result-generated events;
    # the last event per sentence index carries the complete list.
    def ev(words):
        return json.dumps({"payload": {"output": {
            "sentence": {"index": 0, "words": words},
            "type": "sentence-synthesis"}}})
    wbi = {}
    _extract_words(ev([{"text": "你", "begin_time": 0, "end_time": 320}]), wbi)
    _extract_words(ev([{"text": "你", "begin_time": 0, "end_time": 320},
                       {"text": "好", "begin_time": 320, "end_time": 480}]), wbi)
    _extract_words("not json", wbi)          # ignored
    _extract_words(json.dumps({"header": {}}), wbi)  # no sentence — ignored
    out = _to_boundaries(wbi, 10.0)
    assert out == [
        {"text": "你", "offset": 10.0, "duration": 0.32},
        {"text": "好", "offset": 10.32, "duration": pytest.approx(0.16)},
    ]


def test_cosyvoice_boundaries_malformed():
    from backends.cosyvoice import _to_boundaries
    assert _to_boundaries({0: [{"text": "x"}]}, 0.0) == []
    assert _to_boundaries({}, 0.0) == []


def test_minimax_subtitles_sentence_only_or_malformed():
    from backends.minimax import _parse_subtitles
    # Sentence blocks without word data (global-site behavior) are skipped:
    # coarse blocks would regress consumers below their estimation fallback.
    assert _parse_subtitles(
        [{"text": "你好世界。", "time_begin": 0, "time_end": 2000}], 0.0) == []
    assert _parse_subtitles({"unexpected": "dict"}, 0.0) == []
    assert _parse_subtitles(
        [{"timestamped_words": [{"word": "x"}]}], 0.0) == []
