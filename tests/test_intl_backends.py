"""Registry integrity tests for the international backends port.

Covers: providers.json required fields, registry wiring for
elevenlabs/openai/google, env-var validation, and default voices.
"""

import json
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "skills", "ttsCN", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import backends  # noqa: E402

PROVIDERS_JSON = os.path.join(REPO_ROOT, "skills", "ttsCN", "data", "providers.json")

# Fields consumed by _build_backends() plus voices for _build_voices()
REQUIRED_FIELDS = [
    "id", "name", "provider", "env_vars", "import_module", "pip_package",
    "pip_install", "max_chars", "max_duration_sec", "voices_count",
    "supports_ssml", "supports_clone", "cost", "cost_per_10k",
    "max_duration_display", "supports_emotion", "supports_dialects",
    "languages", "streaming", "setup_label", "get_key_url", "tags", "voices",
]

NEW_BACKENDS = {
    "elevenlabs": {"env": ["ELEVENLABS_API_KEY"], "default_voice": "21m00Tcm4TlvDq8ikWAM"},
    "openai": {"env": ["OPENAI_API_KEY"], "default_voice": "alloy"},
    "google": {"env": ["GOOGLE_TTS_API_KEY"], "default_voice": "en-US-Neural2-F"},
}


def _load_providers():
    with open(PROVIDERS_JSON, encoding="utf-8") as f:
        return json.load(f)


def test_every_provider_entry_has_required_fields():
    data = _load_providers()
    for p in data["backends"]:
        missing = [f for f in REQUIRED_FIELDS if f not in p]
        assert not missing, f"{p.get('id', '?')} missing fields: {missing}"
        assert p["voices"], f"{p['id']} has an empty voices list"
        # Every tag must be defined in the tags metadata
        for t in p["tags"]:
            assert t in data["tags"], f"{p['id']} uses undefined tag '{t}'"


def test_registry_has_eleven_backends():
    assert len(backends.BACKENDS) == 11
    for bid in NEW_BACKENDS:
        assert bid in backends.BACKENDS


@pytest.mark.parametrize("bid", sorted(NEW_BACKENDS))
def test_new_backend_registry_wiring(bid):
    info = backends.BACKENDS[bid]
    assert info["env"] == NEW_BACKENDS[bid]["env"]
    assert info["max_chars"] == 400
    assert info["import"][0] == "requests"
    assert info["module"] == "." + bid


@pytest.mark.parametrize("bid", sorted(NEW_BACKENDS))
def test_init_backend_raises_missing_env(bid, monkeypatch):
    for var in NEW_BACKENDS[bid]["env"]:
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(backends.MissingEnvVarError):
        backends.init_backend(bid)


@pytest.mark.parametrize("bid", sorted(NEW_BACKENDS))
def test_init_backend_builds_config_with_env(bid, monkeypatch):
    for var in NEW_BACKENDS[bid]["env"]:
        monkeypatch.setenv(var, "test-key")
    monkeypatch.delenv("TTS_VOICE", raising=False)
    # Ignore any ~/.ttsCN.json on the machine running the tests
    monkeypatch.setattr(backends, "_load_pref", lambda key: None)
    config = backends.init_backend(bid)
    assert config["key"] == "test-key"
    assert config["voice"] == NEW_BACKENDS[bid]["default_voice"]


@pytest.mark.parametrize("bid", sorted(NEW_BACKENDS))
def test_synthesize_func_importable(bid):
    func = backends.get_synthesize_func(bid)
    assert callable(func)
