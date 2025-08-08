"""
OCR Temel Sınıfı - Soyut arayüz tanımı

Tüm OCR motorları bu arayüzü implement etmelidir.
Bu sayede farklı OCR teknolojileri aynı şekilde kullanılabilir.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Tuple
import numpy as np


class BaseOCR(ABC):
    """
    OCR motorları için soyut temel sınıf
    
    Tüm OCR implementasyonları bu sınıftan türetilmelidir.
    Bu sayede sistem genişletilebilir ve değiştirilebilir kalır.
    """
    
    @abstractmethod
    def recognize(self, frame: np.ndarray) -> Iterator[Tuple[Tuple[float, float, float, float], str, float]]:
        """
        Görüntüden metin tanıma işlemi
        
        Args:
            frame (np.ndarray): İşlenecek görüntü karesi
            
        Yields:
            tuple: (bbox, text, confidence) formatında sonuçlar
                - bbox: (x1, y1, x2, y2) sınırlayıcı kutu koordinatları
                - text: Tanınan metin
                - confidence: Güven skoru (0.0-1.0 arası)
        """
        pass
    
    @abstractmethod
    def set_language(self, language: str):
        """
        OCR dilini ayarlar
        
        Args:
            language (str): Dil kodu (örn: 'tr', 'en', 'de')
        """
        pass
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Görüntü ön işleme (opsiyonel)
        
        Alt sınıflar bu metodu override edebilir.
        Varsayılan implementasyon hiçbir şey yapmaz.
        
        Args:
            frame (np.ndarray): Ham görüntü
            
        Returns:
            np.ndarray: İşlenmiş görüntü
        """
        return frame
    
    def postprocess_results(self, results):
        """
        Sonuç son işleme (opsiyonel)
        
        Alt sınıflar OCR sonuçlarını filtrelemek,
        düzenlemek veya iyileştirmek için bu metodu
        override edebilir.
        
        Args:
            results: Ham OCR sonuçları
            
        Returns:
            İşlenmiş sonuçlar
        """
        return results
    
    def get_supported_languages(self) -> list:
        """
        Desteklenen dillerin listesini döner
        
        Returns:
            list: Desteklenen dil kodları
        """
        return ['tr', 'en']  # Varsayılan diller
    
    def get_model_info(self) -> dict:
        """
        Model bilgilerini döner
        
        Returns:
            dict: Model ve sürüm bilgileri
        """
        return {
            'name': self.__class__.__name__,
            'version': 'unknown',
            'supported_languages': self.get_supported_languages()
        }