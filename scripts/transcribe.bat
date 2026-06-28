@echo off
set "PATH=C:\Users\DoctorChungPC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin;%PATH%"
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\transcribe.py %*
