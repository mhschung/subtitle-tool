import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def find_ffmpeg():
    for path in os.environ.get("PATH", "").split(";"):
        candidate = os.path.join(path, "ffmpeg.exe")
        if os.path.isfile(candidate):
            return candidate
    cwd_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
    if os.path.isfile(cwd_ffmpeg):
        return cwd_ffmpeg
    return "ffmpeg"


def check_nvenc(ffmpeg):
    try:
        result = subprocess.run(
            [ffmpeg, "-encoders"], capture_output=True, text=True, timeout=15
        )
        return "h264_nvenc" in result.stdout or "hevc_nvenc" in result.stdout
    except Exception:
        return False


def test_nvenc_works(ffmpeg):
    try:
        r = subprocess.run(
            [ffmpeg, "-f", "lavfi", "-i", "color=c=black:s=64x64:d=1",
             "-c:v", "hevc_nvenc", "-preset", "p7", "-cq", "23",
             "-y", os.devnull],
            capture_output=True, text=True, timeout=30
        )
        return r.returncode == 0
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Burn SRT subtitles into video using GPU or CPU"
    )
    parser.add_argument("video", help="Input video file")
    parser.add_argument("--srt", help="SRT subtitle file", default=None)
    parser.add_argument("-o", "--output", help="Output video path", default=None)
    parser.add_argument("--codec", choices=["h264", "hevc", "auto"], default="auto",
                        help="Video codec (default: auto: nvenc > libx265)")
    parser.add_argument("--cq", type=int, default=23,
                        help="Quality 0-51, lower=better (default: 23)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print ffmpeg command without running")

    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(f"Error: video not found: {args.video}", file=sys.stderr)
        sys.exit(1)

    if args.srt is None:
        base, _ = os.path.splitext(args.video)
        args.srt = base + ".srt"

    if not os.path.isfile(args.srt):
        print(f"Error: SRT not found: {args.srt}", file=sys.stderr)
        sys.exit(1)

    if args.output is None:
        base, ext = os.path.splitext(args.video)
        args.output = f"{base}_subburned.mp4"

    ffmpeg = find_ffmpeg()

    # detect codec
    if args.codec == "auto":
        nvenc_ok = check_nvenc(ffmpeg) and test_nvenc_works(ffmpeg)
        vcodec = "hevc_nvenc" if nvenc_ok else "libx265"
    else:
        nvenc_map = {"hevc": "hevc_nvenc", "h264": "h264_nvenc"}
        vcodec = nvenc_map.get(args.codec, "libx265")
        nvenc_ok = vcodec.endswith("nvenc") and test_nvenc_works(ffmpeg)
        if vcodec.endswith("nvenc") and not nvenc_ok:
            print("Warning: NVENC unavailable, falling back to libx265", file=sys.stderr)
            vcodec = "libx265"

    # copy SRT to temp with ASCII name for filter compatibility
    temp_srt = os.path.join(tempfile.gettempdir(), "_subburner_temp.srt")
    shutil.copy2(args.srt, temp_srt)

    # write filter script (relative path avoids colon/unicode issues on Windows)
    filter_file = os.path.join(tempfile.gettempdir(), "_subburner_filter.txt")
    with open(filter_file, "w", encoding="utf-8") as f:
        f.write("subtitles=_subburner_temp.srt\n")
    temp_cwd = tempfile.gettempdir()

    cmd = [
        ffmpeg, "-i", args.video,
        "-filter_script:v", filter_file,
        "-c:v", vcodec,
    ]
    if vcodec.endswith("nvenc"):
        cmd += ["-preset", "p7", "-cq", str(args.cq)]
    else:
        cmd += ["-crf", str(args.cq)]
    cmd += ["-c:a", "aac", "-b:a", "128k", "-y", args.output]

    print(f"Input:   {os.path.basename(args.video)}")
    print(f"SRT:     {os.path.basename(args.srt)}")
    print(f"Output:  {args.output}")
    print(f"Codec:   {vcodec}  CQ={args.cq}")
    print()

    if args.dry_run:
        print("Dry-run: ffmpeg " + " ".join(str(a) for a in cmd[1:]))
        return

    print("Burning subtitles...")
    try:
        subprocess.run(cmd, check=True, cwd=temp_cwd)
        print(f"\nDone: {args.output}")
    except subprocess.CalledProcessError:
        print("Error: ffmpeg failed. Try --codec hevc or h264.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install ffmpeg or add to PATH.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
