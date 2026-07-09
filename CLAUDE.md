# CLAUDE.md — ttsCN

## Architecture

```
data/providers.json          ← Single source of truth (edit this to add/update providers)
    │
    ├── backends/__init__.py  ← Reads JSON → builds BACKENDS/VOICES at import time
    ├── tts.py                ← CLI: synthesis, --list, schema, --dry-run
    └── build_docs.py         ← Generates docs/index.html + docs/providers.md
```

**Key rule:** Never hardcode backend metadata in `__init__.py` or `tts.py`.
All provider data lives in `data/providers.json`. The Python code reads from it.

## Agent-Native Contract

ttsCN follows the [agent-native-design](https://github.com/Agents365-ai/agent-native-design) specification:

- **stdout** = structured JSON (when `--format json` or non-TTY)
- **stderr** = human-readable diagnostics
- **Exit codes**: 0=ok, 1=internal, 2=validation, 3=auth, 4=backend
- **Envelope**: `{"ok":bool, "data":{...}, "meta":{"version":"...","schema_version":"1.1.0",...}}`
- **Error**: `{"ok":false, "error":{"code":"...","message":"...","retryable":bool,...}}`

## Adding a New TTS Backend

1. Add provider entry to `data/providers.json` (follow existing schema)
2. Create `scripts/backends/<id>.py` with a `synthesize(chunks, config, output_file, output_format)` function
3. Run `python scripts/build_docs.py` to regenerate HTML + Markdown
4. Test: `python scripts/tts.py --dry-run --platform <id> "测试文本"`

## Testing

```bash
# Dry run (no package installs needed)
python scripts/tts.py --dry-run "测试" --platform <id>

# JSON mode
python scripts/tts.py --format json --list | jq .

# Schema introspection
python scripts/tts.py schema backends --fields name,cost,supports_clone

# Exit codes
python scripts/tts.py --format json --platform doubao "test" out.wav; echo $?
# Should return 3 (auth_missing_env) if VOLCENGINE_APPID not set
```

## Conventions

- Backend files in `backends/` must export `synthesize(chunks, config, output_file, output_format)`
- `output_format` is `"wav"` or `"mp3"`
- All backends normalize to 48kHz mono WAV before concat
- Use `output.emit_error()` for all error exits (never `sys.exit` directly)
- Chunk splitting is handled by `tts.py`'s `chunk_text()`; backends receive pre-split chunks
- Backend errors should be raised as `RuntimeError` — caught by `tts.py` and routed through `emit_error`
