from paddleocr import PaddleOCR

ocr = PaddleOCR(

    lang='tr'

)

img_path = r"C:\Users\ASUS\Desktop\videotext\jpgadi.jpg"

results = ocr.predict(img_path)

# Sadece rec_texts alanını yazdır
print(results[0]['rec_texts'])
