# Repository Guidelines

## What This Is

ttsCN is an agent skill for multi-platform Chinese text-to-speech. The agent-facing
entrypoint is `skills/ttsCN/SKILL.md` — read it first: it defines the workflow
(pick backend → pick voice → synthesize → report), the 8 supported backends
(Edge / Doubao / CosyVoice / Azure / Tencent / Baidu / MiniMax / Xunfei), voice
guides, and voice cloning. This file covers what any coding agent needs to use or
modify the repo; Claude Code / OpenClaw read the richer `SKILL.md` natively.

## Project Structure

- `skills/ttsCN/SKILL.md` — skill definition and agent workflow (ships to marketplaces)
- `skills/ttsCN/scripts/tts.py` — CLI entrypoint (synthesis, `--list`, `schema`, `clone`)
- `skills/ttsCN/scripts/backends/` — one module per TTS provider behind a uniform
  `synthesize(chunks, config, output_file, output_format)` interface
- `skills/ttsCN/data/providers.json` — single source of truth for backend metadata
  (costs, voices, env vars, pip packages). Edit this, then regenerate docs with
  `python3 skills/ttsCN/scripts/build_docs.py`
- `skills/ttsCN/docs/` — generated provider comparison page (`providers.html` / `.md`);
  root `docs/` is the generated GitHub Pages copy. Never edit generated files by hand.

## Using the CLI

```bash
# Free default backend (Edge), no API key; requires: pip install edge-tts + ffmpeg
python3 skills/ttsCN/scripts/tts.py "你好世界" output.wav

# Structured JSON envelope on stdout when piped (or --format json); exit codes:
# 0 ok, 1 internal, 2 validation/fixable, 3 auth missing, 4 backend error
python3 skills/ttsCN/scripts/tts.py --list | jq .data.backends
python3 skills/ttsCN/scripts/tts.py schema backends
```

Paid backends read credentials from environment variables only (see `SKILL.md`
"Environment Variables"). Never commit keys.

## Development Conventions

- Python 3.8+, no hard dependency beyond the per-backend pip packages; `ffmpeg` required.
- All CLI exits go through the JSON envelope helpers in `scripts/output.py` —
  never bare `sys.exit(1)` with prose on stdout.
- Adding a backend = new module in `scripts/backends/` + entry in
  `data/providers.json` (including `import_module`, the importable module name,
  distinct from `pip_package`) + regenerate docs.
- Conventional Commits (`feat:`, `fix:`, `docs:`); every change lands via feature
  branch + pull request, never directly on `main`.
- Bilingual docs: keep `README.md` (EN) and `README_CN.md` (CN) in sync.
