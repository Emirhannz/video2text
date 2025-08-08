"""
Video Frame Ayıklayıcı - OpenCV ile video kare çıkarımı

Video dosyasını kare kare okur ve zaman bilgisiyle birlikte döner.
"""

import cv2
import numpy as np
from typing import Iterator, Tuple


class FrameExtractor:
    """
    Video dosyasından belirli aralıklarla kare çıkarır
    
    Özellikler:
    - Bellek verimli generator pattern
    - Zaman bilgisi (timestamp) desteği
    - Esnek kare atlama (step) ayarı
    """
    
    def __init__(self, video_path: str, step: int = 15):
        """
        Args:
            video_path (str): Video dosyası yolu
            step (int): Her kaç karede bir işlem yapılacağı
        """
        self.video_path = video_path
        self.step = max(1, step)  # En az 1 olmalı
        self.cap = None
        
        # Video bilgilerini al
        self._init_video()
    
    def _init_video(self):
        """Video dosyasını aç ve bilgileri al"""
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Video dosyası açılamadı: {self.video_path}")
        
        # Video özellikleri
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        
        print(f"📊 Video bilgileri:")
        print(f"   🎞️  FPS: {self.fps:.2f}")
        print(f"   📏 Toplam kare: {self.frame_count}")
        print(f"   ⏱️  Süre: {self.duration:.2f} saniye")
        print(f"   ⚡ İşlenecek kare: ~{self.frame_count // self.step}")
    
    def __iter__(self) -> Iterator[Tuple[int, np.ndarray, float]]:
        """
        Video karelerini iterator olarak döner
        
        Yields:
            tuple: (kare_indeksi, kare_görüntüsü, zaman_saniye)
        """
        if not self.cap or not self.cap.isOpened():
            self._init_video()
        
        frame_idx = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    break
                
                # Sadece belirtilen adımlarda işlem yap
                if frame_idx % self.step == 0:
                    # Zaman bilgisini al (milisaniye → saniye)
                    timestamp_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
                    timestamp_sec = timestamp_ms / 1000.0
                    
                    yield frame_idx, frame, timestamp_sec
                
                frame_idx += 1
                
        finally:
            self._cleanup()
    
    def get_frame_at_time(self, time_sec: float) -> np.ndarray:
        """
        Belirli bir zamandaki kareyi döner
        
        Args:
            time_sec (float): Saniye cinsinden zaman
            
        Returns:
            np.ndarray: Kare görüntüsü
        """
        if not self.cap or not self.cap.isOpened():
            self._init_video()
        
        # Zaman pozisyonunu ayarla
        self.cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
        ret, frame = self.cap.read()
        
        if not ret:
            raise ValueError(f"Zaman {time_sec:.2f}s'de kare bulunamadı")
        
        return frame
    
    def get_frame_at_index(self, frame_idx: int) -> np.ndarray:
        """
        Belirli indeksteki kareyi döner
        
        Args:
            frame_idx (int): Kare indeksi
            
        Returns:
            np.ndarray: Kare görüntüsü
        """
        if not self.cap or not self.cap.isOpened():
            self._init_video()
        
        # Kare pozisyonunu ayarla
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        
        if not ret:
            raise ValueError(f"Kare indeksi {frame_idx}'de kare bulunamadı")
        
        return frame
    
    def _cleanup(self):
        """Kaynakları temizle"""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def __del__(self):
        """Destructor - kaynakları otomatik temizle"""
        self._cleanup()
    
    def __enter__(self):
        """Context manager desteği"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - temizlik"""
        self._cleanup()