"""
PaddleOCR Wrapper - PaddleOCR 3.1.0 için düzeltilmiş sürüm

PaddleOCR 3.x'in yeni API'sini kullanır.
Türkçe dil desteği ve GPU/CPU optimizasyonu içerir.
"""

import numpy as np
from typing import Iterator, Tuple, List
import cv2

from .base import BaseOCR
# a) en üst kısma ekle
# from .beton import BetonPreprocessor, OtsuConfig



class PaddleOCRWrapper(BaseOCR):
    """
    PaddleOCR 3.1.0 için wrapper sınıfı
    
    Özellikler:
    - PaddleOCR 3.x yeni API desteği
    - Türkçe dil desteği  
    - GPU/CPU seçimi
    - PP-OCRv5 model desteği
    """
    
    def __init__(self, gpu: bool = True):
        """
        Args:
            gpu (bool): GPU kullanımı (varsayılan: True)
        """
        

        self.gpu = gpu
        self.ocr = None
        self._has_logged_resize = False

        
        self._init_ocr()
    
    def _init_ocr(self):
        """PaddleOCR 3.1.0 motorunu başlatır (eski stabil akış)."""
        try:
            from paddleocr import PaddleOCR
            print("🔧 PaddleOCR 3.1.0 başlatılıyor...")
            self.ocr = PaddleOCR(lang="tr", use_angle_cls=True)
            print("🤖 PaddleOCR 3.1.0 başlatıldı (varsayılan ayarlar)")
        except ImportError:
            raise ImportError(
                "PaddleOCR 3.1.0 bulunamadı. Kurulum için:\n"
                "pip install paddlepaddle-gpu==3.1.0 paddleocr==3.1.0"
            )
        except Exception as e:
            print(f"⚠️  PaddleOCR başlatma hatası: {e}")
            self.ocr = None
            return

    def recognize(
        self,
        frame: np.ndarray,
    ) -> Iterator[Tuple[Tuple[float, float, float, float], str, float]]:
        if self.ocr is None:
            self._init_ocr()
            if self.ocr is None:
                return

        # 1) Ön-işleme
        proc = self.preprocess_frame(frame)

    # 2) OCR çağrısı (ESKİ: predict)
        try:
            pages = self.ocr.predict(input=proc)
        except Exception as e:
            print("⚠️  predict hatası:", e)
            return

        if not pages:
            return

    # 3) Sonuçları çözüp yield et
        for page in pages:
            res = page.get("res", page)
            polys  = res.get("dt_polys", [])
            texts  = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])

            for poly, txt, score in zip(polys, texts, scores):
                if not txt or score < 0.30:
                    continue
                xs = [p[0] for p in poly]
                ys = [p[1] for p in poly]
                bbox = (float(min(xs)), float(min(ys)),
                    float(max(xs)), float(max(ys)))
                yield bbox, txt.strip(), float(score)


    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Görüntü ön işleme - OCR kalitesini artırır
        
        Args:
            frame (np.ndarray): Ham görüntü
            
        Returns:
            np.ndarray: İyileştirilmiş görüntü
        """
        if frame is None or frame.size == 0:
            print("⚠️  Boş frame alındı")
            return frame
        
        try:
            # Görüntü boyutu kontrolü
            height, width = frame.shape[:2]
            
            # Çok küçük görüntüleri büyüt (PaddleOCR 3.x için optimize edildi)
            if height < 32 or width < 32:
                scale_factor = max(64/height, 64/width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                if not self._has_logged_resize:
                    print(f"🔍 Frame büyütüldü: {width}x{height} → {new_width}x{new_height}")
                    self._has_logged_resize = True
            
            # Çok büyük görüntüleri küçült (performans ve bellek için)
            elif height > 1080 or width > 1920:
                scale_factor = min(1080/height, 1920/width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                if not self._has_logged_resize:
                    print(f"🔍 Frame küçültüldü: {width}x{height} → {new_width}x{new_height}")
                    self._has_logged_resize = True
            
            # Görüntü kalitesi iyileştirme (isteğe bağlı)
            # frame = cv2.bilateralFilter(frame, 9, 75, 75)  # Gürültü azaltma
            
            return frame
            
        except Exception as e:
            print(f"⚠️  Preprocessing hatası: {e}")
            return frame
    
    def set_language(self, language: str):
        """
        OCR dilini değiştirir - PaddleOCR 3.x'te yeniden başlatma gerekiyor
        
        Not: Bu sürümde dil desteği kaldırılmış - varsayılan model kullanılır
        
        Args:
            language (str): Yeni dil kodu (bu sürümde kullanılmaz)
        """
        print(f"⚠️  Dil değiştirme bu sürümde desteklenmiyor - varsayılan model kullanılır")
    
    def get_supported_languages(self) -> List[str]:
        """
        PaddleOCR 3.x'in desteklediği diller
        
        Returns:
            list: Desteklenen dil kodları
        """
        return [
            'ch', 'en', 'tr', 'french', 'german', 'korean', 'japan',
            'chinese_cht', 'ta', 'te', 'ka', 'latin', 'arabic', 'cyrillic',
            'devanagari', 'hi', 'mr', 'ne', 'ur', 'fa', 'ug', 'th'
        ]
    
    def get_model_info(self) -> dict:
        """
        PaddleOCR 3.1.0 model bilgilerini döner
        
        Returns:
            dict: Model ve yapılandırma bilgileri
        """
        return {
            'name': 'PaddleOCR',
            'version': '3.1.0',
            'language': 'auto',  # Otomatik dil tespiti
            'gpu': self.gpu,
            'supported_languages': self.get_supported_languages(),
            'models': {
                'detection': 'PP-OCRv5_server_det', 
                'recognition': 'PP-OCRv5_server_rec',  # server_rec daha iyi
                'classification': 'PP-LCNet_x1_0_textline_ori'
            },
            'features': {
                'text_detection': True,
                'text_recognition': True,
                'angle_classification': True,
                'multi_language': True,
                'pp_ocrv5': True,
                'auto_download': True,  # Modeller otomatik indiriliyor
            }
        }
    
    def benchmark(self, test_image: np.ndarray, iterations: int = 5) -> dict:
        """
        Performans testi - PaddleOCR 3.x için optimize edildi
        
        Args:
            test_image (np.ndarray): Test görüntüsü
            iterations (int): Test tekrar sayısı (varsayılan: 5)
            
        Returns:
            dict: Performans metrikleri
        """
        import time
        
        times = []
        detection_counts = []
        
        print(f"🧪 PaddleOCR 3.1.0 performans testi ({iterations} iterasyon)...")
        
        # İlk çağrı genelde yavaş oluyor (model yükleme)
        print("🔥 Isınma turu...")
        list(self.recognize(test_image))
        
        for i in range(iterations):
            start_time = time.time()
            results = list(self.recognize(test_image))
            end_time = time.time()
            
            times.append(end_time - start_time)
            detection_counts.append(len(results))
            
            print(f"   {i + 1}/{iterations}: {end_time - start_time:.3f}s, {len(results)} tespit")
        
        avg_time = sum(times) / len(times) if times else 0
        total_detections = sum(detection_counts)
        
        return {
            'paddleocr_version': '3.1.0',
            'avg_time': avg_time,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'avg_detections': sum(detection_counts) / len(detection_counts) if detection_counts else 0,
            'total_iterations': iterations,
            'gpu_enabled': self.gpu,
            'total_detections': total_detections,
            'throughput_fps': 1.0 / avg_time if avg_time > 0 else 0
        }
    
    def check_gpu_availability(self) -> bool:
        """
        GPU kullanılabilirliğini kontrol eder
        
        Returns:
            bool: GPU kullanılabilir mi?
        """
        try:
            import paddle
            return paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
        except:
            return False
    
    def get_model_download_info(self) -> dict:
        """
        İndirilen model bilgilerini döner
        
        Returns:
            dict: Model indirme bilgileri
        """
        return {
            'auto_download': True,
            'cache_dir': '~/.paddlex/official_models',
            'models_downloaded': [
                'PP-LCNet_x1_0_doc_ori',
                'UVDoc', 
                'PP-LCNet_x1_0_textline_ori',
                'PP-OCRv5_server_det',
                'PP-OCRv5_server_rec'  # server_rec daha kaliteli
            ],
            'note': 'Modeller ilk kullanımda otomatik indirilir ve cache\'lenir'
        }