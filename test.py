import queue
import threading
import time

import sounddevice as sd
import soundfile as sf
import whisper
from googletrans import Translator

audio_path = r"D:\VedioLand\audio.wav"
chunk_sec = 2
overlap_sec = 1
prebuffer_sec = 1  # ⭐️ 播放前預留幾秒
model = whisper.load_model("base")
translator = Translator()

audio, sr = sf.read(audio_path)
total_sec = int(len(audio) / sr)
audio_q = queue.Queue(maxsize=50)
stop_flag = threading.Event()
subtitle_list = []


def feeder_thread():
    for start in range(0, total_sec - overlap_sec, chunk_sec):
        if stop_flag.is_set():
            break
        end = min(start + chunk_sec + overlap_sec, total_sec)
        chunk = audio[start * sr : end * sr].astype("float32")
        try:
            audio_q.put((start, chunk), timeout=1)
        except queue.Full:
            print(f"⚠️ 字幕處理太慢，丟棄 {start}~{end}秒")


def asr_thread():
    last_text = ""
    while not stop_flag.is_set() or not audio_q.empty():
        try:
            start, chunk = audio_q.get(timeout=1)
        except queue.Empty:
            continue
        result = model.transcribe(chunk)
        for seg in result["segments"]:
            text = seg["text"].strip()
            if text not in last_text:
                zh = translator.translate(text, dest="zh-tw").text
                print(f"\n⏰ {start:>4}秒: {text} → {zh}")
                subtitle_list.append({"start": start, "text": text, "zh": zh})
                last_text += text


# ----------- 先啟動 feeder 和 asr ---------
t_feed = threading.Thread(target=feeder_thread)
t_asr = threading.Thread(target=asr_thread)
t_feed.start()
t_asr.start()

# ⭐️ 預先等待 N 秒讓 queue 裡先塞資料
print(f"先緩衝 {prebuffer_sec} 秒字幕處理...")
time.sleep(prebuffer_sec)


# ----------- 播放完整音檔 ----------
def play_thread():
    print("開始順播音檔")
    sd.play(audio, sr)
    sd.wait()
    print("音檔播放結束")


t_play = threading.Thread(target=play_thread)
try:
    t_play.start()
    while t_play.is_alive() or t_feed.is_alive() or t_asr.is_alive():
        t_play.join(timeout=0.2)
        t_feed.join(timeout=0.2)
        t_asr.join(timeout=0.2)
except KeyboardInterrupt:
    print("\n偵測到 Ctrl+C，正在優雅結束...")
    stop_flag.set()
    t_play.join()
    t_feed.join()
    t_asr.join()

with open("output.txt", "w", encoding="utf-8") as f:
    for seg in subtitle_list:
        f.write(f"{seg['start']:>4}秒 | {seg['text']} | {seg['zh']}\n")
print("直播模擬同步完成！")
