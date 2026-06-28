---
name: subtitle
description: 影片字幕產生 — 說「產生字幕」「做字幕」「subtitle」時載入
---

安裝方式：將此 SKILL.md 放入 `~/.config/opencode/skills/subtitle/` 目錄。

## 工作流程

當使用者說「產生字幕」時：

1. 確認 `ffmpeg` 已安裝
2. 確認目標影片檔案存在
3. 執行 `scripts/transcribe.py` 進行語音辨識並產出 SRT 字幕
4. 報告字幕檔路徑與內容摘要

## 指令範例

```bash
# 純轉字幕
python scripts/transcribe.py "影片.mp4" --srt

# 轉字幕 + Gemma 4 分析
python scripts/transcribe.py "影片.mp4" --srt --analysis

# 指定 SRT 輸出路徑
python scripts/transcribe.py "影片.mp4" --srt "自訂名稱.srt"

# 輸出 JSON
python scripts/transcribe.py "影片.mp4" --srt --json
```

## 注意事項

- 字幕檔自動存放在影片同目錄，副檔名 `.srt`
- Whisper small 需 ~2GB VRAM；Gemma 4 另需 ~7.6GB
- 支援多國語言（自動偵測）
- 若辨識不準確，可加 `--model medium` 或 `--model large`
