# Subtitle Tool — Whisper + Gemma 4 影片字幕產生器

本機 GPU 加速的影片字幕產生工具。使用 OpenAI Whisper 進行語音辨識，可選用 Gemma 4 進行內容分析。

## 功能

- **影片 → SRT 字幕**：支援 mp4/mkv/avi/mov/webm
- **GPU 加速**：NVIDIA CUDA（Blackwell / Ada / Ampere）
- **Gemma 4 分析**：可選將逐字稿送給本機 Gemma 4 做摘要或問答
- **純本機**：不需任何雲端 API

## 需求

| 元件 | 規格 |
|------|------|
| GPU | NVIDIA 6GB+ VRAM（建議） |
| 系統 | Windows 10+ / Linux / macOS |
| Python | 3.10+ |
| 套件 | 見 `requirements.txt` |

## 安裝

```bash
# 1. 安裝 ffmpeg
# Windows:  winget install ffmpeg
# macOS:    brew install ffmpeg
# Linux:    sudo apt install ffmpeg

# 2. 建立虛擬環境並安裝依賴
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt

# 3. 安裝 CUDA 版 PyTorch（可選，但強烈建議）
# Windows:
pip install torch --index-url https://download.pytorch.org/whl/cu128

# macOS/Linux 請見 pytorch.org
```

## 使用方式

```bash
# 基本：產生 SRT 字幕
scripts\transcribe.bat 影片.mp4 --srt

# 進階：產生字幕 + 分析
scripts\transcribe.bat 影片.mp4 --srt --analysis

# 指定模型（預設 small，可換 medium/large/tiny）
scripts\transcribe.bat 影片.mp4 --model medium --srt

# JSON 輸出
scripts\transcribe.bat 影片.mp4 --srt --json
```

Linux/macOS 請直接呼叫 Python：

```bash
python scripts/transcribe.py 影片.mp4 --srt
```

## 參數說明

| 參數 | 說明 |
|------|------|
| `audio_file` | 影片或音檔路徑 |
| `--model` | Whisper 模型大小：tiny/base/small(預設)/medium/large |
| `--language` | 語言代碼（如 en, zh），預設自動偵測 |
| `--srt` | 輸出 SRT 字幕檔（不加值則自動命名） |
| `--analysis` | 將逐字稿送 Gemma 4 分析 |
| `--prompt` | 自訂分析提示詞 |
| `--json` | JSON 格式輸出 |
| `--gemma-model` | Ollama Gemma 模型名稱 |

## 專案結構

```
subtitle-tool/
├── scripts/
│   ├── transcribe.py     # 主程式
│   └── transcribe.bat    # Windows 批次檔
├── SKILL.md              # OpenCode skill（選擇性安裝）
├── requirements.txt
├── .gitignore
└── README.md
```

## 授權

MIT
