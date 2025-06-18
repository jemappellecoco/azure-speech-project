import os
from pathlib import Path

from dotenv import load_dotenv

from src.azure_speech_project.transcribe import main

# ✅ 正確寫法（使用原始字串或改為 /）
VIDEO_PATH = Path(r"C:\Users\coco\Desktop\S3006742.MXF")
OUTPUT_SRT_PATH = Path(r"C:\Users\coco\Desktop\subtitles.srt")

# ✅ 載入 .env（可選）
load_dotenv()

if __name__ == "__main__":
    import sys
    from unittest.mock import patch

    fake_args = ["transcribe.py", str(VIDEO_PATH), str(OUTPUT_SRT_PATH)]
    with patch.object(sys, "argv", fake_args):
        try:
            main()
            print(f"\n✅ 字幕已產生：{OUTPUT_SRT_PATH}")
        except Exception as e:
            print(f"\n❌ 發生錯誤：{e}")
