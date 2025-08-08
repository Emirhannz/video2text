"""
Video Processor - Videolardan metin çıkarma sistemi

Bu paket, video dosyalarından OCR teknolojisi kullanarak
metin çıkarma işlemlerini gerçekleştirir.

Temel kullanım:
    from video_processor import run_pipeline
    run_pipeline("video.mp4", "output.json")
"""

__version__ = "1.0.0"
__author__ = "Video Processor Team"

# Ana fonksiyonları dışa aktar
from .engine import run_pipeline

__all__ = ["run_pipeline"]