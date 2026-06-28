import argparse
import json
import os
import sys
import urllib.request

import torch
import whisper


def transcribe(audio_path, model_name="base", language=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        print(f"Using GPU: {torch.cuda.get_device_name(0)}", file=sys.stderr)
    model = whisper.load_model(model_name, device=device)
    result = model.transcribe(audio_path, language=language)
    return result


def format_srt(segments):
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _fmt_time(seg["start"])
        end = _fmt_time(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def _fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def analyze_with_gemma(text, prompt):
    data = json.dumps({
        "model": "gemma4:12b",
        "prompt": f"{prompt}\n\n{text}",
        "stream": False,
        "options": {"temperature": 0.1},
    }).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["response"].strip()


def main():
    parser = argparse.ArgumentParser(description="Whisper -> Gemma 4 audio pipeline")
    parser.add_argument("audio_file", help="Path to audio file (wav, mp3, etc.)")
    parser.add_argument("--model", default="small", help="Whisper model size: tiny/base/small/medium/large")
    parser.add_argument("--language", default=None, help="Language code (e.g. en, zh)")
    parser.add_argument("--analysis", action="store_true", help="Send transcription to Gemma 4 for analysis")
    parser.add_argument("--prompt", default="Analyze the following transcription:", help="Prompt for analysis")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--gemma-model", default="gemma4:12b", help="Gemma model name in Ollama")
    parser.add_argument("--srt", nargs="?", const="", default=None, help="Output SRT subtitle file path (default: auto based on input)")
    args = parser.parse_args()

    if not os.path.exists(args.audio_file):
        print(f"Error: file not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)

    result = transcribe(args.audio_file, args.model, args.language)
    text = result["text"].strip()
    segments = result.get("segments", [])

    if args.srt is not None:
        srt_path = args.srt if args.srt else os.path.splitext(args.audio_file)[0] + ".srt"
        srt_content = format_srt(segments)
        os.makedirs(os.path.dirname(srt_path) or ".", exist_ok=True)
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"SRT saved: {srt_path}", file=sys.stderr)

    if args.analysis:
        analysis = analyze_with_gemma(text, args.prompt)
        if args.json:
            print(json.dumps({"transcription": text, "analysis": analysis}, ensure_ascii=False))
        else:
            print("=== Transcription ===")
            print(text)
            print()
            print("=== Analysis ===")
            print(analysis)
    else:
        if args.json:
            print(json.dumps({"transcription": text}, ensure_ascii=False))
        elif not args.srt:
            print(text)


if __name__ == "__main__":
    main()
