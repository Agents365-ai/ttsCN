# ttsCN — 多平台中文语音合成技能

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-6C3C97)](https://claude.ai/code)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-orange)](https://openclaw.ai)
[![SkillsMP](https://img.shields.io/badge/SkillsMP-indexed-blue)](https://skillsmp.com)

[English](README.md)

将中文文本转换为自然语音。**所有后端均可在国内使用**，无需 VPN。

| 特性 | Edge TTS | 豆包 | CosyVoice | Azure |
|------|----------|------|-----------|-------|
| 费用 | **免费** | ~0.2元 | ~0.2元 | ~1美元 |
| API密钥 | 无需 | 需要 | 需要 | 需要 |
| 中文音色 | 20+ | 8 | 7 | 20+ |
| SSML | 支持 | 不支持 | 不支持 | 支持 |
| 配置难度 | 零 | 中 | 易 | 中 |

## 快速开始

```bash
# 安装（默认 Edge 后端 — 免费，无需 API Key）
pip install edge-tts

# 生成语音
python skills/ttsCN/scripts/tts.py "你好世界" output.wav
```

## 后端选择

### Edge TTS（默认 — 免费）
微软 Edge 浏览器 TTS，通过 WebSocket 连接。无需注册，无需 API Key，开箱即用。

### 豆包（字节跳动火山引擎）
优质普通话语音，针对短视频/社交媒体内容优化。

### CosyVoice（阿里云百炼/DashScope）
快速流式语音合成，多种声音风格 — 有声书、教育、客服场景。

### Azure（微软）
企业级语音合成，丰富的 SSML 支持。推荐使用 **eastasia**（东亚）区域。

## 语音示例

```bash
# 女性，温暖（默认）— 通用场景
python skills/ttsCN/scripts/tts.py "你好，欢迎使用语音合成。" default.wav

# 男性，活力 — Vlog、旁白
python skills/ttsCN/scripts/tts.py --voice zh-CN-YunxiNeural "今天我们来聊聊..." vlog.wav

# 男性，深沉 — 纪录片
python skills/ttsCN/scripts/tts.py --voice zh-CN-YunyangNeural "在这片古老的土地上..." doc.wav

# 抖音风格 — 更快、更活泼
python skills/ttsCN/scripts/tts.py --platform doubao --rate +10% "家人们！" douyin.wav

# 有声书 — 温柔女声
python skills/ttsCN/scripts/tts.py --platform cosyvoice --voice longxiaoxia_v3 --input chapter1.txt chapter1.wav
```

## 配置文件

创建 `~/.ttsCN.json` 设置默认值：

```json
{
  "backend": "edge",
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "+5%"
}
```

优先级（从高到低）：CLI 参数 > 项目配置（`.ttsCN.json`）> 用户配置（`~/.ttsCN.json`）> 环境变量 > 内置默认值。

## 安装

### Claude Code
```bash
# 插件市场（推荐）
/plugin install ttsCN@365-skills

# 手动安装
git clone https://github.com/Agents365-ai/ttsCN.git ~/.claude/skills/ttsCN/
```

### OpenClaw
```bash
git clone https://github.com/Agents365-ai/ttsCN.git ~/.openclaw/skills/ttsCN/
```

### SkillsMP
在 [skillsmp.com](https://skillsmp.com) 发现并安装。

## 许可证

[CC BY-NC 4.0](LICENSE) — 禁止商用，转载请注明出处。
