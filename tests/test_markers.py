"""Marker spec: [PAUSE:x] + sound tags, rendering per target."""
from markers import (
    protect_pauses, restore_pauses, render_markers, strip_markers,
)

TEXT = "今天[PAUSE:0.5]天气(chuckle)不错"


def test_render_ssml():
    out = render_markers(TEXT, "ssml")
    assert '<break time="0.5s"/>' in out
    assert "(chuckle)" not in out
    assert "[PAUSE" not in out


def test_render_minimax():
    out = render_markers(TEXT, "minimax")
    assert "<#0.5#>" in out
    assert "(chuckle)" in out  # gating happens in tts.py, not here
    assert "[PAUSE" not in out


def test_render_plain_strips_everything():
    out = render_markers(TEXT, "plain")
    assert out == "今天天气不错"
    assert strip_markers(TEXT) == out


def test_protect_restore_roundtrip():
    protected = protect_pauses(TEXT)
    assert "[PAUSE:0p5]" in protected
    assert "." not in protected.split("(")[0]
    assert restore_pauses(protected) == TEXT


def test_integer_pause_unchanged_by_protection():
    assert protect_pauses("[PAUSE:2]") == "[PAUSE:2]"
    assert render_markers("[PAUSE:2]", "ssml") == '<break time="2s"/>'


def test_azure_style_wrap(monkeypatch):
    from backends.azure import _style_wrap
    monkeypatch.setenv("TTS_STYLE", "gentle")
    assert _style_wrap("<prosody>x</prosody>") == \
        '<mstts:express-as style="gentle"><prosody>x</prosody></mstts:express-as>'
    monkeypatch.delenv("TTS_STYLE")
    assert _style_wrap("<prosody>x</prosody>") == "<prosody>x</prosody>"
