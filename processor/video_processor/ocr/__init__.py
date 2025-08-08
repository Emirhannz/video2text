"""
OCR Modülü - Optik Karakter Tanıma sistemi

Bu modül farklı OCR motorlarını destekler ve
ortak bir arayüz sağlar.
"""

from .base import BaseOCR
from .paddle import PaddleOCRWrapper

__all__ = ["BaseOCR", "PaddleOCRWrapper"]