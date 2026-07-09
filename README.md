# ttsCN — Multi-Platform Chinese TTS Skill

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-6C3C97)](https://claude.ai/code)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-orange)](https://openclaw.ai)
[![SkillsMP](https://img.shields.io/badge/SkillsMP-indexed-blue)](https://skillsmp.com)

[中文文档](README_CN.md)

Generate natural Chinese speech audio from text. **All backends work in China** — no VPN needed.

| Feature | Edge TTS | Doubao | CosyVoice | Azure |
|---------|----------|--------|-----------|-------|
| Cost | **Free** | ~0.2 RMB | ~0.2 RMB | ~1 USD |
| API key | None | Required | Required | Required |
| Chinese voices | 20+ | 8 | 7 | 20+ |
| SSML | Yes | No | No | Yes |
| Setup | Zero | Medium | Easy | Medium |

## Quick Start

```bash
# Install (default Edge backend — free, no API key)
pip install edge-tts

# Generate speech
python skills/ttsCN/scripts/tts.py "你好世界" output.wav
```

## Backends

### Edge TTS (Default — Free)
Microsoft Edge TTS via WebSocket. No API key, no registration, works everywhere.

### Doubao (ByteDance Volcano Ark)
Premium Mandarin voices optimized for short video / social media content.

### CosyVoice (Alibaba DashScope)
Fast streaming TTS with diverse voice styles — audiobooks, education, customer service.

### Azure (Microsoft)
Enterprise-grade TTS with rich SSML support. Use **eastasia** region for China.

## Voice Examples

```bash
# Female, warm (default) — general purpose
python skills/ttsCN/scripts/tts.py "你好，欢迎使用语音合成。" default.wav

# Male, energetic — vlog, narration
python skills/ttsCN/scripts/tts.py --voice zh-CN-YunxiNeural "今天我们来聊聊..." vlog.wav

# Male, deep — documentary
python skills/ttsCN/scripts/tts.py --voice zh-CN-YunyangNeural "在这片古老的土地上..." doc.wav

# Douyin style — faster, livelier
python skills/ttsCN/scripts/tts.py --platform doubao --rate +10% "家人们！" douyin.wav
```

## Config File

Create `~/.ttsCN.json` for defaults:

```json
{
  "backend": "edge",
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "+5%"
}
```

## Install

### Claude Code
```bash
# Plugin marketplace (recommended)
/plugin install ttsCN@365-skills

# Manual
git clone https://github.com/Agents365-ai/ttsCN.git ~/.claude/skills/ttsCN/
```

### OpenClaw
```bash
git clone https://github.com/Agents365-ai/ttsCN.git ~/.openclaw/skills/ttsCN/
```

### SkillsMP
Discover and install at [skillsmp.com](https://skillsmp.com).

## License

[CC BY-NC 4.0](LICENSE) — Free for non-commercial use. Commercial use requires permission.
