import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def process_video_with_nvenc():
    # 1. 初始化 Tkinter 並隱藏主視窗（我們只需要對話框）
    root = tk.Tk()
    root.withdraw()

    # 2. 彈出對話框：選擇來源影片
    messagebox.showinfo("步驟 1", "請選擇要處理的「來源影片」檔案。")
    video_path = filedialog.askopenfilename(
        title="選擇影片檔案",
        filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov")]
    )
    if not video_path:
        print("已取消選擇影片。")
        return

    # 3. 彈出對話框：選擇 SRT 字幕檔
    messagebox.showinfo("步驟 2", "請選擇對應的「SRT 字幕」檔案。")
    srt_path = filedialog.askopenfilename(
        title="選擇字幕檔案",
        filetypes=[("Subtitle Files", "*.srt")]
    )
    if not srt_path:
        print("已取消選擇字幕。")
        return

    # 4. 彈出對話框：選擇儲存位置與檔名
    messagebox.showinfo("步驟 3", "請設定「輸出影片」的儲存位置與名稱。")
    output_path = filedialog.asksaveasfilename(
        title="儲存輸出影片",
        defaultextension=".mp4",
        filetypes=[("MP4 Video", "*.mp4")]
    )
    if not output_path:
        print("已取消儲存。")
        return

    # 5. 處理 FFmpeg 在 Windows 上的路徑格式問題
    # FFmpeg 的 subtitles 濾鏡對 Windows 的路徑（反斜線 \ 與磁碟機冒號 :）非常敏感
    # 必須將 \ 換成 /，並將磁碟機冒號 : 加上跳脫字元 \:
    safe_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")

    # 6. 建構 NVIDIA 硬體加速的 FFmpeg 指令
    command = [
        "ffmpeg",
        "-hwaccel", "cuda",                # 啟用 CUDA 硬體加速解碼
        "-i", video_path,                  # 輸入影片
        "-vf", f"subtitles='{safe_srt_path}'", # 燒錄字幕
        "-c:v", "h264_nvenc",              # 使用 NVIDIA 顯示卡進行硬體編碼
        "-c:a", "copy",                    # 音軌直接複製，節省資源
        "-y",                              # 若輸出檔案已存在則直接覆蓋
        output_path
    ]

    # 7. 執行指令
    print("\n🚀 開始透過 RTX 顯示卡加速轉檔，請稍候...")
    try:
        # 使用 subprocess 執行，並將輸出導向終端機以便查看進度
        subprocess.run(command, check=True)
        print("\n✅ 轉檔完成！")
        messagebox.showinfo("完成", f"硬字幕燒錄成功！\n檔案已儲存於：\n{output_path}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 發生錯誤：{e}")
        messagebox.showerror("錯誤", "轉檔過程中發生錯誤，請檢查終端機的錯誤訊息。")

# 執行主程式
if __name__ == "__main__":
    process_video_with_nvenc()