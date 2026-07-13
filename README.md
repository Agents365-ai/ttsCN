# ttsCN — Multi-Platform Chinese TTS Skill

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Agents365-ai/ttsCN?style=flat&logo=github)](https://github.com/Agents365-ai/ttsCN/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Agents365-ai/ttsCN?style=flat&logo=github)](https://github.com/Agents365-ai/ttsCN/network/members)
[![Latest Release](https://img.shields.io/github/v/release/Agents365-ai/ttsCN?logo=github)](https://github.com/Agents365-ai/ttsCN/releases/latest)
[![Last Commit](https://img.shields.io/github/last-commit/Agents365-ai/ttsCN?logo=github)](https://github.com/Agents365-ai/ttsCN/commits/main)

[![SkillsMP](https://img.shields.io/badge/SkillsMP-listed-1f6feb)](https://skillsmp.com)
[![ClawHub](https://img.shields.io/badge/ClawHub-listed-ff6b35)](https://clawhub.ai)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-8a2be2)](https://github.com/Agents365-ai/365-skills)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-2ea44f)](https://agentskills.io)

[中文文档](README_CN.md)

Generate natural Chinese speech audio from text. **All backends work in China** — no VPN needed.

Works with Claude Code, Cursor, Codex, Copilot, Windsurf, Cline / Roo Code, Gemini CLI,
Aider, Zed, OpenCode, OpenClaw / ClawHub, Hermes, pi-mono — plus major Chinese agents
(Trae, Qwen Code / Tongyi Lingma, Baidu Comate, CodeGeeX) — and any agent that reads
the [Agent Skills](https://agentskills.io) format.

| Feature | Edge TTS | Doubao | CosyVoice | Azure |
|---------|----------|--------|-----------|-------|
| Cost (per 10K chars) | **Free** | ~1 RMB | ~2 RMB | ~$1/M chars |
| API key | None | Required | Required | Required |
| Chinese voices | 20+ | 8 | 7 | 20+ |
| SSML | Yes | No | No | Yes |
| Setup | Zero | Medium | Easy | Medium |

Full 8-backend comparison (incl. Tencent / Baidu / MiniMax / Xunfei): [docs/providers.md](skills/ttsCN/docs/providers.md)

## Pipeline

<img src="assets/workflow.png" width="450" alt="ttsCN Workflow">

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

## Voice Cloning

Clone your own voice and use it by name (built-in for MiniMax and CosyVoice):

```bash
# MiniMax — local audio file, paid (~$1.5/voice), confirm with --yes
python skills/ttsCN/scripts/tts.py clone create --platform minimax --audio my.wav --name myvoice --yes

# CosyVoice — free enrollment, audio must be a public URL (10-20s)
python skills/ttsCN/scripts/tts.py clone create --platform cosyvoice --audio https://example.com/my.wav --name myvoice

# Speak with your voice
python skills/ttsCN/scripts/tts.py "用我的声音说这句话" out.wav --platform minimax --voice myvoice
```

`clone list` / `clone delete --name X` manage stored voices (`~/.ttsCN.json`). Only clone voices you own or are authorized to use. Note: MiniMax deletes clones unused for 7 days; CosyVoice voices expire after 1 year unused.

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
```

Or tell your coding agent:
> help me to install https://github.com/Agents365-ai/ttsCN.git

```bash
# Manual — copy the inner skill folder (SKILL.md must sit at the install root)
git clone https://github.com/Agents365-ai/ttsCN.git /tmp/ttsCN
cp -r /tmp/ttsCN/skills/ttsCN ~/.claude/skills/ttsCN
```

### OpenClaw
```bash
git clone https://github.com/Agents365-ai/ttsCN.git /tmp/ttsCN
cp -r /tmp/ttsCN/skills/ttsCN ~/.openclaw/skills/ttsCN
```

### SkillsMP
Discover and install at [skillsmp.com](https://skillsmp.com).

## Support

If this project helps you, feel free to support the author:

<table>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/wechat-pay.png" width="180" alt="WeChat Pay">
      <br>
      <b>WeChat Pay</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/alipay.png" width="180" alt="Alipay">
      <br>
      <b>Alipay</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/buymeacoffee.png" width="180" alt="Buy Me a Coffee">
      <br>
      <b>Buy Me a Coffee</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/awarding/award.gif" width="180" alt="Reward">
      <br>
      <b>Reward</b>
    </td>
  </tr>
</table>

## Author

**Agents365-ai**

- Bilibili: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai

## License

[CC BY-NC 4.0](LICENSE) — Free for non-commercial use. Commercial use requires permission.
