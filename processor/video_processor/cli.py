"""
Komut Satırı Arayüzü - Video işleme için CLI

Kullanım:
    python -m video_processor.cli -v video.mp4 -o output.json
    python -m video_processor.cli --video sample.mp4 --step 10 --cpu
"""

import argparse
import sys
import os
from pathlib import Path

from .engine import run_pipeline


def build_parser():
    """Komut satırı argüman parser'ını oluşturur"""
    parser = argparse.ArgumentParser(
        prog="video-processor",
        description="🎬 Video dosyalarından metin çıkarma aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım örnekleri:
  %(prog)s -v video/sample.mp4 -o report.json
  %(prog)s --video test.mp4 --step 10 --cpu
  %(prog)s -v input.avi -o results.json --step 30
        """)
    
    # Ana argümanlar
    parser.add_argument(
        "-i", "--video",
        default="video/sarki.mp4",
        help="İşlenecek video dosyası (varsayılan: video/2kvideo.mp4)")
    
    parser.add_argument(
        "-o", "--out",
        default="report.json",
        help="Çıktı JSON dosyası (varsayılan: report.json)")
    
    # İşlem parametreleri
    parser.add_argument(
        "--step",
        type=int,
        default=15,
        help="Her kaç karede bir işlem yapılacağı (varsayılan: 15)")
    
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="CPU kullan (varsayılan: GPU kullanır)")
    
    # Yardımcı seçenekler
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Detaylı çıktı göster")
    
    return parser


def validate_inputs(args):
    """Giriş argümanlarını doğrular"""
    errors = []
    
    # Video dosyası kontrolü
    if not os.path.exists(args.video):
        errors.append(f"❌ Video dosyası bulunamadı: {args.video}")
    
    # Çıktı dizini kontrolü
    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
            print(f"📁 Çıktı dizini oluşturuldu: {out_dir}")
        except OSError as e:
            errors.append(f"❌ Çıktı dizini oluşturulamadı: {e}")
    
    # Step parametresi kontrolü
    if args.step <= 0:
        errors.append("❌ Step değeri pozitif bir sayı olmalıdır")
    
    return errors


def main():
    """Ana CLI fonksiyonu"""
    parser = build_parser()
    args = parser.parse_args()
    
    # Banner göster
    print("🎬 Video Processor v1.0")
    print("=" * 40)
    
    # Argümanları doğrula
    errors = validate_inputs(args)
    if errors:
        print("\n".join(errors))
        return 1
    
    # Parametreleri göster
    print(f"📹 Video: {args.video}")
    print(f"📄 Çıktı: {args.out}")
    print(f"⚙️  Step: {args.step}")
    print(f"🖥️  İşlemci: {'CPU' if args.cpu else 'GPU'}")
    print("-" * 40)
    
    try:
        # Pipeline'ı çalıştır
        run_pipeline(
            video_path=args.video,
            out_path=args.out,
            step=args.step,
            gpu=not args.cpu
        )
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ Dosya bulunamadı: {e}")
        return 1
    except ImportError as e:
        print(f"❌ Gerekli kütüphane bulunamadı: {e}")
        print("💡 pip install paddlepaddle paddleocr opencv-python komutunu çalıştırın")
        return 1
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())