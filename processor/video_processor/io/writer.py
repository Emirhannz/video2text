"""
JSON Kaydedici - OCR sonuçlarını JSON formatında yazar

OCR sonuçlarını zaman bilgisi ve konum verileriyle birlikte
yapılandırılmış JSON formatında kaydeder.
"""

import json
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime

OUTPUT_DIR = r"C:\Users\ASUS\Desktop\videotext\processor\output"

class JsonWriter:
    """
    OCR sonuçlarını JSON formatında kaydeder
    
    Özellikler:
    - UTF-8 desteği (Türkçe karakterler)
    - Yapılandırılmış veri formatı
    - Metadata bilgileri
    - Performans optimizasyonu
    """
    
    def __init__(self, output_path: str):
        """
        Args:
            output_path (str): Çıktı JSON dosyası yolu
        """
        self.output_path = output_path
        self.data: List[Dict[str, Any]] = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "total_detections": 0,
            "processing_info": {}
        }
        
        # Çıktı dizinini oluştur
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    def add(self, timestamp: float, bbox: Tuple[float, float, float, float], 
            text: str, confidence: float):
        """
        OCR sonucunu veri listesine ekler
        
        Args:
            timestamp (float): Saniye cinsinden zaman
            bbox (tuple): Sınırlayıcı kutu koordinatları (x1, y1, x2, y2)
            text (str): Tanınan metin
            confidence (float): Güven skoru (0.0-1.0)
        """
        x1, y1, x2, y2 = bbox
        
        detection = {
            "timestamp": round(timestamp, 3),
            "bbox": {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "width": int(x2 - x1),
                "height": int(y2 - y1)
            },
            "text": text.strip(),
            "confidence": round(confidence, 4),
            "text_length": len(text.strip()),
            "detection_id": len(self.data) + 1
        }
        
        self.data.append(detection)
        self.metadata["total_detections"] += 1
    
    def add_metadata(self, key: str, value: Any):
        """
        Metadata bilgisi ekler
        
        Args:
            key (str): Metadata anahtarı
            value (Any): Metadata değeri
        """
        self.metadata["processing_info"][key] = value
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        İşlem istatistiklerini döner
        
        Returns:
            dict: İstatistik bilgileri
        """
        if not self.data:
            return {"message": "Henüz veri yok"}
        
        confidences = [d["confidence"] for d in self.data]
        text_lengths = [d["text_length"] for d in self.data]
        timestamps = [d["timestamp"] for d in self.data]
        
        stats = {
            "total_detections": len(self.data),
            "confidence_stats": {
                "min": min(confidences),
                "max": max(confidences),
                "avg": sum(confidences) / len(confidences)
            },
            "text_length_stats": {
                "min": min(text_lengths),
                "max": max(text_lengths),
                "avg": sum(text_lengths) / len(text_lengths)
            },
            "time_range": {
                "start": min(timestamps),
                "end": max(timestamps),
                "duration": max(timestamps) - min(timestamps)
            },
            "high_confidence_count": len([c for c in confidences if c > 0.8]),
            "unique_texts": len(set(d["text"] for d in self.data))
        }
        
        return stats
    
    def filter_by_confidence(self, min_confidence: float = 0.5):
        """
        Düşük güven skorlu sonuçları filtreler
        
        Args:
            min_confidence (float): Minimum güven skoru
        """
        original_count = len(self.data)
        self.data = [d for d in self.data if d["confidence"] >= min_confidence]
        filtered_count = original_count - len(self.data)
        
        if filtered_count > 0:
            print(f"🔍 {filtered_count} düşük güvenli sonuç filtrelendi")
            self.metadata["total_detections"] = len(self.data)
    
    def remove_duplicates(self, time_threshold: float = 1.0, similarity_threshold: float = 0.9):
        """
        Benzer metinleri temizler
        
        Args:
            time_threshold (float): Zaman eşiği (saniye)
            similarity_threshold (float): Benzerlik eşiği
        """
        if len(self.data) <= 1:
            return
        
        from difflib import SequenceMatcher
        
        filtered_data = []
        
        for current in self.data:
            is_duplicate = False
            
            for existing in filtered_data:
                # Zaman farkı kontrolü
                time_diff = abs(current["timestamp"] - existing["timestamp"])
                if time_diff > time_threshold:
                    continue
                
                # Metin benzerlik kontrolü
                similarity = SequenceMatcher(None, 
                                           current["text"].lower(), 
                                           existing["text"].lower()).ratio()
                
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    # Daha yüksek güven skorlu olanı tut
                    if current["confidence"] > existing["confidence"]:
                        filtered_data.remove(existing)
                        filtered_data.append(current)
                    break
            
            if not is_duplicate:
                filtered_data.append(current)
        
        removed_count = len(self.data) - len(filtered_data)
        self.data = filtered_data
        
        if removed_count > 0:
            print(f"🧹 {removed_count} tekrar eden sonuç temizlendi")
            self.metadata["total_detections"] = len(self.data)
    
    def finalize(self, include_stats: bool = True, pretty_print: bool = True):
        """
        Veriyi JSON dosyasına yazar ve işlemi tamamlar
        
        Args:
            include_stats (bool): İstatistikleri dahil et
            pretty_print (bool): Okunabilir format kullan
        """
        if include_stats:
            self.metadata["statistics"] = self.get_statistics()
        
        # Son metadata güncellemeleri
        self.metadata["completed_at"] = datetime.now().isoformat()
        self.metadata["output_file"] = os.path.abspath(self.output_path)
        
        # JSON yapısı
        output_data = {
            "metadata": self.metadata,
            "detections": self.data
        }
        
        # Dosyayı yaz
        with open(self.output_path, "w", encoding="utf-8") as f:
            if pretty_print:
                json.dump(output_data, f, ensure_ascii=False, indent=2, sort_keys=True)
            else:
                json.dump(output_data, f, ensure_ascii=False, separators=(',', ':'))
        
        print(f"💾 JSON dosyası kaydedildi: {self.output_path}")
        
        # Özet bilgi göster
        if self.data:
            stats = self.get_statistics()
            print(f"📊 Toplam tespit: {stats['total_detections']}")
            print(f"⏱️  Zaman aralığı: {stats['time_range']['duration']:.2f}s")
            print(f"🎯 Ortalama güven: {stats['confidence_stats']['avg']:.3f}")

    def _format_mmss(self, seconds: float, show_ms: bool = False) -> str:
        """Saniyeyi [MM:SS] formatına çevirir."""
        if seconds is None:
            return "[00:00]"
        total_ms = int(round(seconds * 1000))
        mm, ss = divmod(total_ms // 1000, 60)
        if show_ms:
            ms = total_ms % 1000
            return f"[{mm:02d}:{ss:02d}.{ms:03d}]"
        return f"[{mm:02d}:{ss:02d}]"

    OUTPUT_DIR = r"C:\Users\ASUS\Desktop\videotext\processor\output"

    def export_grouped_text(self, text_file_path: str = None, sep: str = " | ", show_ms: bool = False):
        """
        Aynı zamana ait tespitleri tek satırda birleştirir:
        [MM:SS] - TXT1 | TXT2 | ...
        """
        # Yol belirtilmediyse veya sadece dosya adı geldiyse output klasörüne ata
        if not text_file_path:
            text_file_path = self.output_path.replace('.json', '_frames.txt')
        elif not os.path.isabs(text_file_path):
            text_file_path = os.path.join(OUTPUT_DIR, text_file_path)

        os.makedirs(os.path.dirname(text_file_path), exist_ok=True)

        from collections import OrderedDict
        buckets: "OrderedDict[float, list[str]]" = OrderedDict()

        for d in sorted(self.data, key=lambda x: x["timestamp"]):
            ts = d["timestamp"]
            txt = d["text"].strip()
            if not txt:
                continue
            if ts not in buckets:
                buckets[ts] = []
            buckets[ts].append(txt)

        with open(text_file_path, "w", encoding="utf-8") as f:
            for ts, texts in buckets.items():
                stamp = self._format_mmss(ts, show_ms=show_ms)
                line = f"{stamp} - {sep.join(texts)}"
                f.write(line + "\n")

        print(f"📄 Kare bazlı metin dosyası: {text_file_path}")

        
    
    def export_text_only(self, text_file_path: str = None):
        """
        Sadece metinleri basit txt dosyasına yazar
        
        Args:
            text_file_path (str): Metin dosyası yolu (opsiyonel)
        """
        if not text_file_path:
            text_file_path = self.output_path.replace('.json', '_texts.txt')
        
        with open(text_file_path, "w", encoding="utf-8") as f:
            for detection in sorted(self.data, key=lambda x: x["timestamp"]):
                timestamp = detection["timestamp"]
                text = detection["text"]
                confidence = detection["confidence"]
                
                f.write(f"[{timestamp:7.2f}s] {text} (güven: {confidence:.3f})\n")
        
        print(f"📄 Metin dosyası: {text_file_path}")


    