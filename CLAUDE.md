# ttsCN

Multi-platform Chinese TTS skill. 8 backends (Edge/Doubao/CosyVoice/Azure/Tencent/Baidu/MiniMax/Xunfei), all work in China.

## Structure
- `skills/ttsCN/SKILL.md` — skill definition
- `skills/ttsCN/scripts/` — TTS generation scripts
- `skills/ttsCN/data/` — voice data and presets
- `skills/ttsCN/docs/` — documentation

## Key conventions
- Python 3.8+, `ffmpeg` required
- 8 TTS backends with env-var-based auth
- Output: audio files (MP3/WAV) via ffmpeg
