from ultralytics import YOLO
import pytesseract
from database import add_parking_log, update_parking_log
from datetime import datetime
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MODEL_PATH = r'C:\Users\muham\PycharmProjects\Otopark_Sistemi\plate-detector.pt'
model = YOLO(MODEL_PATH)

def validate_turkish_plate(plate_text):
    """
    Türk plakalarını doğrulayan bir fonksiyon.
    """
    plate_pattern = r'^[0-9]{2}[A-Z]{1,3}[0-9]{1,4}$'  # Türk plaka formatı
    plate_text = re.sub(r'[^A-Z0-9]', '', plate_text.upper().strip())  # Temizlik yap
    if re.match(plate_pattern, plate_text):
        return plate_text
    return None

def process_plate(image):
    """
    YOLO modeli ve Tesseract OCR ile plaka algılar ve giriş/çıkış işlemi yapar.
    """
    results = model.predict(source=image, save=False, save_txt=False)
    plates = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Koordinatları al
            cropped_img = image[y1:y2, x1:x2]  # Plaka bölgesini kırp

            # Tesseract ile OCR işlemi yap
            plate_text = pytesseract.image_to_string(cropped_img, config='--psm 7').strip()
            validated_plate = validate_turkish_plate(plate_text)  # Türk plakasını doğrula
            if validated_plate:
                plates.append(validated_plate)
                handle_vehicle_entry_exit(validated_plate)  # Giriş/çıkış işlemi yap
            else:
                print(f"Geçersiz plaka tespit edildi: {plate_text}")

    return plates

def handle_vehicle_entry_exit(plate_text):
    """
    Araç giriş/çıkış işlemini yönetir.
    """
    from database import get_all_parking_logs

    logs = get_all_parking_logs()
    for log in logs:
        if log[1] == plate_text and log[3] is None:  # Çıkışı olmayan kayıt varsa
            exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            fee = calculate_fee(log[2])
            update_parking_log(plate_text, exit_time, fee)
            print(f"Plaka {plate_text} çıkış yaptı. Çıkış Saati: {exit_time}, Ücret: {fee} TL")
            return

    # Yeni giriş
    entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    add_parking_log(plate_text, entry_time)
    print(f"Plaka {plate_text} giriş yaptı. Giriş Saati: {entry_time}")

def calculate_fee(entry_time):
    """
    Araç giriş-çıkış süresine göre ücret hesaplar.
    """
    entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
    duration = (datetime.now() - entry_time).total_seconds() / 3600  # Saat cinsinden
    return round(duration * 10, 2)  # Saatlik 10 TL ücret