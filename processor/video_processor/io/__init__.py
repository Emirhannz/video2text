"""
IO Modülü - Dosya giriş/çıkış işlemleri

Bu modül video okuma ve sonuç yazma işlemlerini yönetir.
"""

from .extractor import FrameExtractor
from .writer import JsonWriter

__all__ = ["FrameExtractor", "JsonWriter"]