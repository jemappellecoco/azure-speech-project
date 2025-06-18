# Azure Speech Project

This small project demonstrates how to transcribe a video file using
Azure Speech Service and save the result as an SRT subtitle file.

## Setup

1. Install the dependencies:
   ```bash
   pip install azure-cognitiveservices-speech python-dotenv
   ```
2. Create a `.env` file next to your script with the following variables:
   ```
   SPEECH_KEY=your-azure-speech-key
   SPEECH_REGION=your-service-region
   ```
3. Ensure `ffmpeg` is installed and available in your `PATH` for converting
   video files to audio.

## Usage

Run the module directly and pass the video file and the desired SRT output:

```bash
python -m azure_speech_project path/to/video.mp4 subtitles.srt
```

The script will extract the audio from the video, send it to Azure Speech
Service for transcription and create the `subtitles.srt` file with time
codes.
