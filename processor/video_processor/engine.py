"""
Ana Motor (Pipeline) - Tüm sistemi uçtan uca zincirler

Video karelerini okur → OCR uygular → sonuçları kaydeder
"""

from .io.extractor import FrameExtractor
from .ocr.paddle import PaddleOCRWrapper
from .io.writer import JsonWriter


def run_pipeline(video_path, out_path, *, step=15, gpu=True):
    """
    Video işleme pipeline'ını çalıştırır
    
    Args:
        video_path (str): İşlenecek video dosyasının yolu
        out_path (str): Çıktı JSON dosyasının yolu
        step (int): Her kaç karede bir işlem yapılacağı (varsayılan: 15)
        gpu (bool): GPU kullanımı (varsayılan: True)
    
    Returns:
        None
    """
    print(f"🎬 Video yükleniyor: {video_path}")
    extractor = FrameExtractor(video_path, step)
    
    print(f"🤖 OCR motoru başlatılıyor (GPU: {gpu})")
    ocr = PaddleOCRWrapper(gpu)
    
    print(f"📝 Çıktı dosyası: {out_path}")
    writer = JsonWriter(out_path)
    
    frame_count = 0
    text_count = 0
    
    print("🔄 İşlem başlıyor...")
    
    for idx, frame, ts in extractor:
        frame_count += 1
        
        # Her karedeki metinleri tanı
                # Her karedeki metinleri tanı
        results = list(ocr.recognize(frame))
        for bbox, txt, conf in results:
            writer.add(ts, bbox, txt, conf)
            text_count += 1

        # Canlı çıktı → her karede bir satırda yaz
        texts = [txt.strip() for _, txt, _ in results if txt.strip()]
        
        def _fmt_mmss(s):
            total_ms = int(round(s * 1000))
            mm, ss = divmod(total_ms // 1000, 60)
            return f"[{mm:02d}:{ss:02d}]"

        if texts:
            joined = " | ".join(texts)
            print(f"  {_fmt_mmss(ts)} - {joined}")
        else:
            print(f"  {_fmt_mmss(ts)} - (metin yok)")
        

        
        # İlerleme göstergesi
        if frame_count % 10 == 0:
            print(f"  📊 İşlenen kare: {frame_count}, Bulunan metin: {text_count}")
    
    # Sonuçları kaydet
        # JSON yazma yerine: metin dosyası olarak kaydet (.txt)
    import os
    basename = os.path.splitext(os.path.basename(video_path))[0]
    text_output = f"{basename}.txt"
    writer.export_grouped_text(text_file_path=text_output, sep=" | ", show_ms=False)

    
    print(f"✅ İşlem tamamlandı!")
    print(f"   📈 Toplam kare: {frame_count}")
    print(f"   📝 Toplam metin: {text_count}")
    print(f"   💾 Sonuç dosyası: {text_output}")



def run_pipeline_advanced(video_path, out_path, *, step=15, gpu=True, 
                         min_confidence=0.5, filter_duplicates=True):
    """
    Gelişmiş pipeline - gelecekteki özellikler için rezerve
    
    Args:
        video_path (str): Video dosyası yolu
        out_path (str): Çıktı dosyası yolu
        step (int): Kare atlama adımı
        gpu (bool): GPU kullanımı
        min_confidence (float): Minimum güven skoru
        filter_duplicates (bool): Tekrar eden metinleri filtrele
    """
    # Şimdilik basit pipeline'ı çağır
    # İleride buraya filtreleme, önişleme vs. eklenebilir
    run_pipeline(video_path, out_path, step=step, gpu=gpu)