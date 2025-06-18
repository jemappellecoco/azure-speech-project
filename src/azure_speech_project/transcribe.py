import os
import subprocess
import time
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv


def convert_video_to_wav(video_path: Path, wav_path: Path) -> None:
    """Convert a video file to wav audio using ffmpeg."""

    # ✅ 使用完整路徑，避免系統找不到 ffmpeg
    FFMPEG_PATH = (
        r"C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"  # ← 這裡改成你實際的路徑
    )

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        str(wav_path),
    ]
    subprocess.run(cmd, check=True)


def seconds_to_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def transcribe_wav_to_srt(
    wav_path: Path, srt_path: Path, speech_key: str, service_region: str
) -> None:
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    speech_config.output_format = speechsdk.OutputFormat.Detailed
    speech_config.request_word_level_timestamps()

    # ✅ 直接指定語言為 zh-TW
    speech_config.speech_recognition_language = "zh-TW"

    audio_input = speechsdk.AudioConfig(filename=str(wav_path))
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_input
    )

    results = []
    done = False

    def recognized(evt: speechsdk.SpeechRecognitionEventArgs):
        nonlocal results
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            offset = evt.result.offset / 10**7
            duration = evt.result.duration / 10**7
            text = evt.result.text
            results.append((offset, offset + duration, text))

    def stop(evt):
        nonlocal done
        done = True

    recognizer.recognized.connect(recognized)
    recognizer.session_stopped.connect(stop)
    recognizer.canceled.connect(stop)

    recognizer.start_continuous_recognition()
    while not done:
        time.sleep(0.5)
    recognizer.stop_continuous_recognition()

    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, (start, end, text) in enumerate(results, 1):
            f.write(f"{idx}\n")
            f.write(f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n")
            f.write(f"{text}\n\n")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Transcribe a video to SRT using Azure Speech Service"
    )
    parser.add_argument("video", type=Path, help="Path to the input video file")
    parser.add_argument("output", type=Path, help="Path to the output SRT file")
    args = parser.parse_args()

    load_dotenv()
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_SERVICE_REGION")
    if not speech_key or not service_region:
        raise RuntimeError(
            "SPEECH_KEY and SPEECH_REGION must be set in environment or .env"
        )

    wav_path = args.output.with_suffix(".wav")
    convert_video_to_wav(args.video, wav_path)
    transcribe_wav_to_srt(wav_path, args.output, speech_key, service_region)
    wav_path.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        print("❌ 發生錯誤：", e)
        traceback.print_exc()
