"""Phoneme application: Azure SSML tags and MiniMax pinyin annotations."""
import json

import pytest

from phonemes import (
    load_phonemes, pinyin_to_sapi, apply_phonemes, apply_phonemes_minimax,
)
from backends.azure import build_ssml_fragment


def test_pinyin_to_sapi_tone_marks():
    assert pinyin_to_sapi("zhí xíng qì") == "zhi 2 xing 2 qi 4"


def test_pinyin_to_sapi_numbered():
    assert pinyin_to_sapi("hang2 zhang3") == "hang 2 zhang 3"


def test_apply_phonemes_azure_ssml():
    out = apply_phonemes("这位行长很忙", {"行长": "hang2 zhang3"})
    assert '<phoneme alphabet="sapi" ph="hang 2 zhang 3">行长</phoneme>' in out


def test_apply_phonemes_minimax_annotation():
    out = apply_phonemes_minimax("去重庆", {"重庆": "chóng qìng"})
    assert out == "去重(chong2)庆(qing4)"


def test_apply_phonemes_minimax_skips_syllable_mismatch():
    # 2 chars but 3 syllables — fail-safe: leave default pronunciation
    out = apply_phonemes_minimax("去重庆", {"重庆": "chong2 qing4 x5"})
    assert out == "去重庆"


def test_load_phonemes_drops_comment_keys(tmp_path):
    p = tmp_path / "ph.json"
    p.write_text(json.dumps({"_comment": "x", "行长": "hang2 zhang3"}),
                 encoding="utf-8")
    assert load_phonemes(str(p)) == {"行长": "hang2 zhang3"}


def test_load_phonemes_rejects_non_object(tmp_path):
    p = tmp_path / "ph.json"
    p.write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_phonemes(str(p))


def test_azure_ssml_fragment_escapes_and_renders():
    frag = build_ssml_fragment(
        "行长说 A&B[PAUSE:0.5]很好(chuckle)", {"行长": "hang2 zhang3"})
    assert '<break time="0.5s"/>' in frag
    assert '<phoneme alphabet="sapi" ph="hang 2 zhang 3">行长</phoneme>' in frag
    assert "A&amp;B" in frag          # plain text is XML-escaped
    assert "(chuckle)" not in frag    # sound tags stripped for azure
    assert "&lt;break" not in frag    # generated tags survive the escape
