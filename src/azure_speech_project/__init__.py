"""Simple utilities to transcribe videos using Azure Speech."""

from .transcribe import convert_video_to_wav, transcribe_wav_to_srt

__all__ = ["convert_video_to_wav", "transcribe_wav_to_srt"]
